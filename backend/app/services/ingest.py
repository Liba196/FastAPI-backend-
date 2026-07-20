from pypdf import PdfReader
from pdf2image import convert_from_path
from PIL import ImageEnhance
import pytesseract
import re
import time  # Ensure this is imported at the top of your file

# If Tesseract isn't on your PATH, uncomment and adjust this line:
# pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

MIN_TEXT_LENGTH = 20   # below this, we assume the page has no real text layer
OCR_CONFIG = "--oem 1 --psm 3"   # LSTM engine only, assume a single text block
BINARIZE_THRESHOLD = 140         # tune this per document if needed


def preprocess_for_ocr(image, threshold: int = BINARIZE_THRESHOLD):
    """
    Grayscale + contrast boost + binarization (pure black/white).
    This is the combination that tested best for our scanned Amharic
    documents — it suppressed most stamp/seal noise while keeping the
    printed text sharp.
    """
    gray = image.convert("L")
    contrast_boosted = ImageEnhance.Contrast(gray).enhance(2.0)

    def threshold_pixel(pixel: int) -> int:
        return 0 if pixel < threshold else 255

    binarized = contrast_boosted.point(threshold_pixel, mode="1")
    return binarized


def clean_ocr_text(text: str) -> str:
    """
    Strips low-value junk lines that OCR tends to produce around
    stamps, seals, signatures, and page decorations.
    """
    cleaned_lines = []
    for line in text.split("\n"):
        stripped = line.strip()
        if not stripped:
            continue
        letters = sum(1 for ch in stripped if ch.isalpha())
        if letters < max(3, len(stripped) * 0.4):
            continue
        cleaned_lines.append(stripped)
    return "\n".join(cleaned_lines)


def extract_text(pdf_path: str) -> list[dict]:
    reader = PdfReader(pdf_path)
    pages = []
    pages_needing_ocr = []

    for i, page in enumerate(reader.pages):
        text = (page.extract_text() or "").strip()
        pages.append({"page_number": i + 1, "text": text})
        if len(text) < MIN_TEXT_LENGTH:
            pages_needing_ocr.append(i + 1)

    if pages_needing_ocr:
        print(f"Pages needing OCR: {pages_needing_ocr}")
        for page_num in pages_needing_ocr:
            # Render ONLY this one page, not the whole document — keeps
            # peak memory to roughly one page's worth instead of all of them.
            page_images = convert_from_path(
                pdf_path, dpi=300, first_page=page_num, last_page=page_num
            )
            raw_image = page_images[0]
            processed_image = preprocess_for_ocr(raw_image)
            ocr_text = pytesseract.image_to_string(
                processed_image, lang="amh+eng", config=OCR_CONFIG
            )
            pages[page_num - 1]["text"] = clean_ocr_text(ocr_text)
            del page_images, raw_image, processed_image  # free immediately, don't wait for GC

    pages = filter_toc_pages(pages)
    return pages
    


def is_real_sentence_end(text: str, pos: int, ender: str) -> bool:
    """
    pos is the index immediately AFTER the candidate ender.
    A bare '.' following a digit (or followed by a digit) is almost
    always Amharic legal numbering — "42.", "38.2", "50.1" — not a
    real sentence boundary, so we filter those out specifically.
    ፡፡, !, and ? don't have this ambiguity in this document.
    """
    if ender != ".":
        return True

    ender_start = pos - len(ender)
    if ender_start > 0 and text[ender_start - 1].isdigit():
        return False  # preceded by a digit -> "42." style numbering
    if pos < len(text) and text[pos].isdigit():
        return False  # followed by a digit -> "38.2" style sub-numbering

    return True


def find_chunk_end(text: str, start: int, max_chars: int, search_window: int = 300) -> int:
    """
    Looks backward from the target cut point for the nearest REAL
    sentence ending, skipping over false positives like numbering.
    """
    ideal_end = start + max_chars
    if ideal_end >= len(text):
        return len(text)

    window_start = max(start, ideal_end - search_window)
    window = text[window_start:ideal_end]

    best_pos = -1
    for ender in ["፡፡", "!", "?", "."]:
        search_limit = len(window)
        while True:
            pos = window.rfind(ender, 0, search_limit)
            if pos == -1:
                break
            candidate = window_start + pos + len(ender)
            if is_real_sentence_end(text, candidate, ender):
                best_pos = max(best_pos, candidate)
                break  # found a valid one for this ender, stop scanning it
            search_limit = pos  # that one was a false positive — keep looking earlier

    return best_pos if best_pos != -1 else ideal_end


def chunk_text(pages: list[dict], max_chars: int = 1000, overlap: int = 150) -> list[dict]:
    """
    Splits document text into overlapping chunks that end on real
    sentence boundaries where possible, spanning page boundaries.
    """
    if overlap >= max_chars:
        raise ValueError("overlap must be smaller than max_chars, or chunking will never terminate")

    full_text = ""
    page_boundaries = []
    for page in pages:
        page_boundaries.append((len(full_text), page["page_number"]))
        full_text += page["text"].strip() + " "

    def page_for_offset(offset: int) -> int:
        page_num = page_boundaries[0][1]
        for boundary_offset, p in page_boundaries:
            if offset >= boundary_offset:
                page_num = p
            else:
                break
        return page_num

    chunks = []
    start = 0
    min_chunk_size = max_chars // 4

    while start < len(full_text):
        end = find_chunk_end(full_text, start, max_chars)
        chunk_str = full_text[start:end].strip()

        if chunk_str:
            if len(chunk_str) < min_chunk_size and chunks:
                chunks[-1]["text"] += " " + chunk_str
            else:
                chunks.append({
                    "page_number": page_for_offset(start),
                    "text": chunk_str,
                })

        # Advance relative to where we actually cut, not the fixed max_chars —
        # important now that `end` varies. Guard against near-zero progress
        # if a sentence end happened to land very close to `start`.
        next_start = end - overlap
        start = next_start if next_start > start else end

    return chunks


if __name__ == "__main__":
    pages = extract_text("backend/documents/sample.pdf")
    for p in pages:
        print(f"Page {p['page_number']}: {len(p['text'])} characters extracted")

    print("\n--- Preview of page 1 ---")
    print(pages[0]["text"][:500])

    chunks = chunk_text(pages)
    print(f"\nProduced {len(chunks)} chunks")
    print("--- First chunk ---")
    print(chunks[0]["text"][:300])



def is_toc_like_page(text: str) -> bool:
    """
    Heuristically detects Table-of-Contents-style pages, which are
    dominated by dot-leaders, page-number references, and heavily
    fragmented OCR tokens rather than real prose. These pages are
    never valid citation sources and pollute vector search with
    keyword-matching noise, so we exclude them entirely rather than
    try to clean them.
    """
    if not text.strip():
        return False

    tokens = text.split()
    if not tokens:
        return False

    digit_ratio = sum(ch.isdigit() for ch in text) / max(1, len(text))
    short_token_ratio = sum(1 for t in tokens if len(t) <= 2) / len(tokens)
    dot_leader_hits = len(re.findall(r"[.\-+፡]{3,}", text))

    score = 0
    if digit_ratio > 0.08:
        score += 1
    if short_token_ratio > 0.30:
        score += 1
    if dot_leader_hits >= 2:
        score += 1

    return score >= 2


def filter_toc_pages(pages: list[dict]) -> list[dict]:
    """
    Marks detected ToC pages as empty text (reusing chunk_text's
    existing 'skip empty pages' logic) rather than deleting them
    outright, so page numbering stays intact and this is easy to
    audit/undo later.
    """
    filtered = []
    excluded_pages = []

    for page in pages:
        if is_toc_like_page(page["text"]):
            excluded_pages.append(page["page_number"])
            filtered.append({"page_number": page["page_number"], "text": ""})
        else:
            filtered.append(page)

    if excluded_pages:
        print(f"Excluded {len(excluded_pages)} Table-of-Contents-like page(s): {excluded_pages}")

    return filtered
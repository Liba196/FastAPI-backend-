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
    """
    Hybrid extraction: try pypdf's fast native text extraction first;
    for any page that comes back empty (a strong sign it's a scanned
    image), fall back to OCR (with preprocessing + cleanup) for just
    that page.
    """
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
        images = convert_from_path(pdf_path, dpi=300)
        for page_num in pages_needing_ocr:
            raw_image = images[page_num - 1]
            processed_image = preprocess_for_ocr(raw_image)
            ocr_text = pytesseract.image_to_string(
                processed_image, lang="amh+eng", config=OCR_CONFIG
            )
            pages[page_num - 1]["text"] = clean_ocr_text(ocr_text)

    return pages


def chunk_text(pages: list[dict], max_chars: int = 1000, overlap: int = 150) -> list[dict]:
    """
    Splits document text into overlapping chunks, treating the whole
    document as one continuous string so chunks can span page boundaries.
    Each chunk still records which page it mostly came from, for citations.
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
        end = start + max_chars
        chunk_str = full_text[start:end].strip()

        if chunk_str:
            if len(chunk_str) < min_chunk_size and chunks:
                chunks[-1]["text"] += " " + chunk_str
            else:
                chunks.append({
                    "page_number": page_for_offset(start),
                    "text": chunk_str,
                })

        start += max_chars - overlap

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


    
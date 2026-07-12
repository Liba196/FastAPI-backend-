from pdf2image import convert_from_path
from PIL import ImageEnhance
import pytesseract

# Only render page 1 — much faster than the whole document
images = convert_from_path("backend/documents/sample.pdf", dpi=300, first_page=1, last_page=1)
original = images[0]
original.save("ocr_debug_original.png")

# Variant A: grayscale + contrast only (no binarization)
gray = original.convert("L")
contrast_only = ImageEnhance.Contrast(gray).enhance(2.0)
contrast_only.save("ocr_debug_contrast_only.png")

# Variant B: grayscale + contrast + binarized (pure black/white)
# Note: binarization can sometimes hurt curvy scripts like Amharic if the
# threshold is wrong — thin strokes can disappear entirely. That's why
# we're testing both variants rather than assuming binarization is better.
binarized = contrast_only.point(lambda x: 0 if x < 140 else 1, mode="1")# type: ignore
binarized.save("ocr_debug_binarized.png")

config = "--oem 1 --psm 3"

print("=== Original (no preprocessing) ===")
print(pytesseract.image_to_string(original, lang="amh+eng", config=config)[:400])

print("\n=== Contrast only ===")
print(pytesseract.image_to_string(contrast_only, lang="amh+eng", config=config)[:400])

print("\n=== Contrast + Binarized ===")
print(pytesseract.image_to_string(binarized, lang="amh+eng", config=config)[:400])
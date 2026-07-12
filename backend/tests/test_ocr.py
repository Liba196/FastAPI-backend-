from app.services.ingestion.pdf_to_images import pdf_to_images
from app.services.ingestion.ocr import extract_text

pages = pdf_to_images("documents/sample.pdf")

print(f"Pages: {len(pages)}")

text = extract_text(pages[0]["image"])

print(text)
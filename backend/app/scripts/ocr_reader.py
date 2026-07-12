from app.services.ingestion.pdf_to_images import pdf_to_images
from app.services.ingestion.ocr import extract_text


def extract_pages(pdf_path):

    pages = pdf_to_images(pdf_path)

    results = []

    for page in pages:

        results.append({
            "page_number": page["page_number"],
            "text": extract_text(page["image"])
        })

    return results
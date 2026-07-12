from pypdf import PdfReader


def extract_pages(pdf_path: str) -> list[dict]:
    """
    Extract text from a PDF page by page.

    Returns:
        [
            {
                "page_number": 1,
                "text": "..."
            }
        ]
    """

    pages = []

    document = PdfReader(pdf_path)

    for page_index, page in enumerate(document.pages):
        pages.append(
            {
                "page_number": page_index + 1,
                "text": page.extract_text() or ""
            }
        )

    return pages 

    
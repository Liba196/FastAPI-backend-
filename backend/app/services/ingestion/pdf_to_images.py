import fitz
from PIL import Image
import io


def pdf_to_images(pdf_path: str):

    document = fitz.open(pdf_path)

    pages = []

    for page_number, page in enumerate(document , start=1):

        pix = page.get_pixmap(dpi=300)

        image = Image.open(io.BytesIO(pix.tobytes("png")))

        pages.append({
            "page_number": page_number,
            "image": image
        })

    document.close()

    return pages
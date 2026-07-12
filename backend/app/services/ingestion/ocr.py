import pytesseract
from PIL import Image

# Tesseract configuration
# --oem 3 : Use the best available OCR engine
# --psm 6 : Assume a single uniform block of text
TESSERACT_CONFIG = "--oem 3 --psm 6"


def extract_text(image: Image.Image, language: str = "amh") -> str:
    """
    Extract text from a PIL image using Tesseract OCR.

    Args:
        image (PIL.Image): Preprocessed image.
        language (str): OCR language (default: Amharic).

    Returns:
        str: Extracted text.
    """

    text = pytesseract.image_to_string(
        image,
        lang=language,
        config=TESSERACT_CONFIG
    )

    return text.strip()
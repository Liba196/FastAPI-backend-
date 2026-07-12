import cv2
import numpy as np
from PIL import Image


def preprocess_image(image: Image.Image) -> Image.Image:
    # PIL -> OpenCV
    img = np.array(image)

    # Convert to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)

    # Remove small noise
    gray = cv2.medianBlur(gray, 3)

    # Convert to pure black & white
    _, thresh = cv2.threshold(
        gray,
        0,
        255,
        cv2.THRESH_BINARY + cv2.THRESH_OTSU
    )

    # OpenCV -> PIL
    return Image.fromarray(thresh)
import re

PATTERNS_TO_REMOVE = [
    r"Page\s+\d+",
    r"ገጽ\s*\d+",
]


def clean_text(text: str) -> str:

    text = text.strip()

    text = text.replace("\r\n", "\n")

    text = re.sub(r"[ \t]+", " ", text)

    text = re.sub(r"\n{3,}", "\n\n", text)

    for pattern in PATTERNS_TO_REMOVE:
        text = re.sub(pattern, "", text, flags=re.IGNORECASE)

    return text.strip()

    PATTERNS_TO_REMOVE = [
    r"Official Seal",
]
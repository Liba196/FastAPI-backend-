import re

ARTICLE_PATTERN = re.compile(
    r"(?=Article\s+\d+|አንቀጽ\s+\d+)",
    re.IGNORECASE
)


def chunk_text(text: str):

    chunks = ARTICLE_PATTERN.split(text)

    chunks = [chunk.strip() for chunk in chunks if chunk.strip()]

    return chunks
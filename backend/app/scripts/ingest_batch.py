"""
ingest_batch.py
Administrative script to ingest multiple PDF documents in one run.
Stand-in for the Phase 10 admin panel's upload feature — run manually
from the terminal until that UI exists.

Fill in DOCUMENTS below with each file's name (must already be sitting
in documents/) and its real, official title, then run this from the
backend/ folder:
    python -m app.scripts.ingest_batch
"""
import os

from app.services.embed_and_store import ingest_document

DOCUMENTS_DIR = "documents"

DOCUMENTS = [
    {
        "filename": "sample.pdf",
        "title": "Private Organizations Employees' Pension Implementation Directive No. 01/2016",
    },
    # {
    #     "filename": "pdf",
    #     "title": "REPLACE WITH THIS DOCUMENT'S REAL OFFICIAL TITLE",
    # },
    # Add the remaining 8 the same way — filename + real title, one per file.
]


def main():
    succeeded, failed = [], []

    for doc in DOCUMENTS:
        pdf_path = os.path.join(DOCUMENTS_DIR, doc["filename"])

        if not os.path.exists(pdf_path):
            print(f"SKIPPING: {pdf_path} not found on disk.")
            failed.append((doc["filename"], "file not found"))
            continue

        print(f"\n{'='*60}\nIngesting: {doc['filename']}\n{'='*60}")
        try:
            ingest_document(pdf_path, title=doc["title"])
            succeeded.append(doc["filename"])
        except Exception as e:
            # One bad document (corrupt file, OCR failure, an API error
            # that exhausts its retries) should never take down the
            # whole batch. Log it, keep going, report everything at the end.
            print(f"FAILED: {doc['filename']} -> {e}")
            failed.append((doc["filename"], str(e)))

    print(f"\n{'='*60}\nBATCH SUMMARY\n{'='*60}")
    print(f"Succeeded ({len(succeeded)}): {succeeded}")
    print(f"Failed ({len(failed)}):")
    for filename, error in failed:
        print(f"  - {filename}: {error}")


if __name__ == "__main__":
    main()
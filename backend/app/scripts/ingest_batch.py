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
        "filename": "pension-proclamation-final-one.pdf",
        "title": "ፌደራል ነጋሪት ጋዜጣ - የግል ድርጅት ሠራተኞች ጡረታ አዋጅ  1268/2022 ",
    },
     {
        "filename": "POESSA-proclamation-715-2003-PDF.pdf",
        "title": "የግል ድርጅት ሠራተኞች ጡረታ አዋጅ  715/2011 ",
    },
     {
        "filename": "Proc.No_.908-2015-Privet-Org.Emp_.SSAAmenedemenetProc.pdf",
        "title": "የግል ድርጅት ሰራተኞች ጡረታ አዋጅን ለማሻሻል የወጣ አዋጅ",
    },
     {
        "filename": "መመሪያ-ቁጥር-05-2016.pdf",
        "title": "የጡረታ መዋጮ የመክፈል ግዴታቸውን ያልተወጡ የግል ድርጅቶች ሃብት የሚከበርበት ፣ የሚያዝበት እና እዳ የሚሰበብሰብበት አፈጻጸም መመሪያ ",
    },
     {
        "filename": "መመሪያ-ቁጥር-06-2016 (1).pdf",
        "title": "የግል ድርጅት ሰራተኞች ጡረታ መዋጮ ገቢ እቅድ አዘገጃጀት ፣ አሰባሰብ ፣ ትልልፍና ቁጥጥር መመሪያ ",
    }, {
        "filename": "የአስተዳደር-መመሪያ-2016.pdf",
        "title": "የሰራተኞች አስተዳደር መመሪያ ቁጥር 03/2016",
    }, {
        "filename": "የጡረታ-አፈጻጸም-መመሪያ-ቁጥር-01-2016.pdf",
        "title": "የጡረታ-አፈጻጸም-መመሪያ-ቁጥር-01/2016",
    }, {
        "filename": "የጡረታ-አፈጻጸም-ማንዋል (1).pdf",
        "title": "የግል ድርጅት ሰራተኞች ጡረታ አፈጻጸም ማኑዋል",
    }, 
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
# backend/app/api/documents.py
import os
import shutil

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, UploadFile, Form
import psycopg

from app.core.deps import require_role
from app.services.embed_and_store import ingest_document, DB_URL
from app.api.document_schemas import DocumentResponse

from fastapi.responses import FileResponse

router = APIRouter(prefix="/api/v1/admin/documents", tags=["documents"])

UPLOADS_DIR = "uploads"
os.makedirs(UPLOADS_DIR, exist_ok=True)


@router.post("", status_code=202)
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile,
    title: str = Form(...),
    user=Depends(require_role("super_admin", "content_editor")),
):
    # Fix 1 & 2: Ensure filename exists and fallback to string to satisfy os.path.join
    filename = file.filename or ""
    if not filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are accepted")

    dest_path = os.path.join(UPLOADS_DIR, filename)

    # Reject duplicates outright
    with psycopg.connect(DB_URL) as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id FROM documents WHERE source_filename = %s",
                (dest_path,),
            )
            if cur.fetchone():
                raise HTTPException(
                    status_code=409,
                    detail=f"A document with filename '{filename}' already exists. "
                           f"Rename the file or delete the existing document first.",
                )

    # Save the uploaded file to disk
    with open(dest_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    # Pre-create the document row synchronously
    with psycopg.connect(DB_URL) as conn:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO documents (title, source_filename) VALUES (%s, %s) RETURNING id",
                (title, dest_path),
            )
            
            # Fix 3: Safely unpack the row to satisfy the type checker
            row = cur.fetchone()
            if not row:
                raise HTTPException(status_code=500, detail="Failed to create document record")
                
            document_id = row[0]
        conn.commit()

    background_tasks.add_task(ingest_document, dest_path, title)

    return {
        "document_id": document_id,
        "status": "pending",
        "message": "Upload received, ingestion started in the background",
    }
@router.get("", response_model=list[DocumentResponse])
def list_documents(user=Depends(require_role("super_admin", "content_editor"))):
    with psycopg.connect(DB_URL) as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id, title, source_filename, status, error_message FROM documents ORDER BY id"
            )
            rows = cur.fetchall()

    return [
        DocumentResponse(
            id=row[0], title=row[1], source_filename=row[2], status=row[3], error_message=row[4]
        )
        for row in rows
    ]


@router.get("/{document_id}", response_model=DocumentResponse)
def get_document(document_id: int, user=Depends(require_role("super_admin", "content_editor"))):
    with psycopg.connect(DB_URL) as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id, title, source_filename, status, error_message FROM documents WHERE id = %s",
                (document_id,),
            )
            row = cur.fetchone()

    if not row:
        raise HTTPException(status_code=404, detail="Document not found")

    return DocumentResponse(
        id=row[0], title=row[1], source_filename=row[2], status=row[3], error_message=row[4]
    )


@router.delete("/{document_id}", status_code=204)
def delete_document(document_id: int, user=Depends(require_role("super_admin"))):
    with psycopg.connect(DB_URL) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT id, source_filename FROM documents WHERE id = %s", (document_id,))
            row = cur.fetchone()

            if not row:
                raise HTTPException(status_code=404, detail="Document not found")

            source_filename = row[1]

            # DB row + its chunks (cascade)
            cur.execute("DELETE FROM documents WHERE id = %s", (document_id,))
            conn.commit()

    # Also remove the file from disk if it was an API upload (lives in uploads/).
    # Manually-ingested docs (documents/) are intentionally left alone — those
    # are hand-curated source files, not something this endpoint should touch.
    if source_filename.startswith("uploads"):
        try:
            os.remove(source_filename)
        except OSError as e:
            print(f"Warning: DB row deleted but failed to remove file {source_filename}: {e}")


@router.get("/{document_id}/file")
def get_document_file(
    document_id: int,
    user=Depends(require_role("super_admin", "content_editor")),
):
    with psycopg.connect(DB_URL) as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT source_filename FROM documents WHERE id = %s",
                (document_id,),
            )
            row = cur.fetchone()

    if not row:
        raise HTTPException(status_code=404, detail="Document not found")

    file_path = row[0]

    if not os.path.exists(file_path):
        raise HTTPException(
            status_code=404,
            detail=f"Document record exists but file is missing from disk: {file_path}",
        )

    return FileResponse(
        file_path,
        media_type="application/pdf",
        filename=os.path.basename(file_path),
    )

@router.post("/{document_id}/retry", status_code=202)
def retry_ingestion(
    document_id: int,
    background_tasks: BackgroundTasks,
    user=Depends(require_role("super_admin", "content_editor")),
):
    with psycopg.connect(DB_URL) as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT title, source_filename, status FROM documents WHERE id = %s",
                (document_id,),
            )
            row = cur.fetchone()

    if not row:
        raise HTTPException(status_code=404, detail="Document not found")

    title, source_filename, status = row

    if status not in ("failed", "processing"):
        raise HTTPException(
            status_code=400,
            detail=f"Document is currently '{status}' — retry is only meaningful for 'failed' or stuck 'processing' documents.",
        )

    if not os.path.exists(source_filename):
        raise HTTPException(
            status_code=404,
            detail=f"Cannot retry: source file no longer exists on disk at {source_filename}",
        )

    background_tasks.add_task(ingest_document, source_filename, title)

    return {"document_id": document_id, "status": "processing", "message": "Retry started"}
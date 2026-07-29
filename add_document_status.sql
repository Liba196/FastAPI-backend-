-- add_document_status.sql
ALTER TABLE documents
    ADD COLUMN status TEXT NOT NULL DEFAULT 'pending'
        CHECK (status IN ('pending', 'processing', 'done', 'failed')),
    ADD COLUMN error_message TEXT,
    ADD COLUMN updated_at TIMESTAMPTZ NOT NULL DEFAULT now();
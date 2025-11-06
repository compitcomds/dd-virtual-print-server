import sqlite3
from datetime import datetime
from typing import Literal, TypedDict, Optional

FileStatus = Literal["uploaded", "converted", "failed", "success", "downloaded"]

DB_PATH = "ocr.db"

class FileRecord(TypedDict):
    file_id: str
    ps_path: str
    pdf_path: Optional[str]
    status: FileStatus
    created_at: str
    certificate_id: Optional[str]
    log_message: Optional[str]
    retry: int

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS files (
            file_id TEXT PRIMARY KEY,
            ps_path TEXT NOT NULL,
            pdf_path TEXT,
            status TEXT NOT NULL CHECK (status IN ('uploaded', 'converted', 'failed', 'success', 'downloaded')),
            created_at TEXT NOT NULL,
            certificate_id TEXT,
            log_message TEXT,
            retry INTEGER NOT NULL DEFAULT 0
        )
    """)
    conn.commit()
    conn.close()

def add_file_record(file_id: str, ps_path: str):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        INSERT INTO files (file_id, ps_path, pdf_path, status, created_at, certificate_id, log_message, retry)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (file_id, ps_path, None, "uploaded", datetime.now().isoformat(), None, None, 0))
    conn.commit()
    conn.close()

def update_file_record(
    file_id: str,
    ps_path: Optional[str] = None,
    pdf_path: Optional[str] = None,
    status: Optional[FileStatus] = None,
    certificate_id: Optional[str] = None,
    log_message: Optional[str] = None,
    retry: Optional[int] = None
):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # Build dynamic UPDATE query
    updates = []
    values = []
    
    if ps_path is not None:
        updates.append("ps_path = ?")
        values.append(ps_path)
    if pdf_path is not None:
        updates.append("pdf_path = ?")
        values.append(pdf_path)
    if status is not None:
        updates.append("status = ?")
        values.append(status)
    if certificate_id is not None:
        updates.append("certificate_id = ?")
        values.append(certificate_id)
    if log_message is not None:
        updates.append("log_message = ?")
        values.append(log_message)
    if retry is not None:
        updates.append("retry = ?")
        values.append(retry)
    
    if not updates:
        conn.close()
        return
    
    values.append(file_id)
    query = f"UPDATE files SET {', '.join(updates)} WHERE file_id = ?"
    
    c.execute(query, values)
    conn.commit()
    conn.close()

def get_file_record(file_id: str) -> Optional[FileRecord]:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("""
        SELECT *
        FROM files
        WHERE file_id = ?
    """, (file_id,))
    row = c.fetchone()
    conn.close()
    return dict(row) if row else None

def get_next_processing_record() -> Optional[FileRecord]:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    
    # Get record with retry < 3
    c.execute("""
        SELECT *
        FROM files
        WHERE (status = 'uploaded' OR status = 'converted') AND retry < 4
        ORDER BY datetime(created_at) ASC
        LIMIT 1
    """)
    row = c.fetchone()    
    result = dict(row) if row else None
    conn.close()
    return result
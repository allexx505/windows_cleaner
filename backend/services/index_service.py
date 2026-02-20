"""
File index: SQLite storage and full-scan with batching and low priority.
Used for large-file and rule-based scans. USN used for incremental when available.
"""
import os
import sqlite3
import threading
import time
from pathlib import Path
from typing import Iterator

from backend.core.constants import (
    BATCH_DIRS_BEFORE_SLEEP,
    BATCH_SLEEP_SECONDS,
    INDEX_DB_DIR,
    INDEX_DB_NAME,
    MAX_RESULTS_PAGE,
)
from backend.services.resource_guard import is_under_load, throttle_if_needed


def _db_path() -> str:
    Path(INDEX_DB_DIR).mkdir(parents=True, exist_ok=True)
    return os.path.join(INDEX_DB_DIR, INDEX_DB_NAME)


def _get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(_db_path())
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS file_index (
            path TEXT PRIMARY KEY,
            volume TEXT NOT NULL,
            size_bytes INTEGER NOT NULL,
            mtime_ns INTEGER NOT NULL,
            is_dir INTEGER NOT NULL
        )
        """
    )
    conn.execute("CREATE INDEX IF NOT EXISTS idx_volume ON file_index(volume)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_size ON file_index(size_bytes)")
    return conn


_lock = threading.Lock()


def ensure_index_schema() -> None:
    """Create index table if not exists."""
    with _lock:
        conn = _get_connection()
        conn.close()


def full_scan_directory(
    root_path: str,
    min_size_bytes: int = 0,
    extensions: list[str] | None = None,
    yield_batch: bool = True,
) -> Iterator[tuple[str, int, int, bool]]:
    """
    Walk directory and yield (path, size_bytes, mtime_ns, is_dir).
    Batched with sleep and resource guard; low priority is caller's responsibility
    (run in background thread). extensions: e.g. ['.mp4','.avi'] or None for all.
    """
    root_path = os.path.normpath(root_path)
    if not os.path.isdir(root_path):
        return
    count = 0
    ext_set = None
    if extensions:
        ext_set = {e.lower() if e.startswith(".") else "." + e.lower() for e in extensions}
    for dirpath, _dirnames, filenames in os.walk(root_path, topdown=True):
        if yield_batch:
            count += 1
            if count >= BATCH_DIRS_BEFORE_SLEEP:
                count = 0
                time.sleep(BATCH_SLEEP_SECONDS)
            if is_under_load():
                throttle_if_needed()
        for name in filenames:
            try:
                full = os.path.join(dirpath, name)
                st = os.stat(full, follow_symlinks=False)
                if not hasattr(st, "st_file_attributes") or (st.st_file_attributes & 0x400 == 0):
                    size = st.st_size
                    if ext_set and Path(name).suffix.lower() not in ext_set:
                        continue
                    if size >= min_size_bytes:
                        yield full, size, st.st_mtime_ns, False
            except OSError:
                pass


def index_full_scan_volume(volume: str, root: str) -> int:
    """
    Full scan one volume root and upsert into SQLite. Returns number of rows updated.
    Uses batching and resource guard internally.
    """
    ensure_index_schema()
    updated = 0
    batch = []
    batch_size = 5000
    with _lock:
        conn = _get_connection()
        try:
            for path, size_bytes, mtime_ns, is_dir in full_scan_directory(
                root, yield_batch=True
            ):
                batch.append((path, volume, size_bytes, mtime_ns, 0))
                if len(batch) >= batch_size:
                    conn.executemany(
                        """
                        INSERT OR REPLACE INTO file_index (path, volume, size_bytes, mtime_ns, is_dir)
                        VALUES (?,?,?,?,?)
                        """,
                        batch,
                    )
                    conn.commit()
                    updated += len(batch)
                    batch = []
            if batch:
                conn.executemany(
                    """
                    INSERT OR REPLACE INTO file_index (path, volume, size_bytes, mtime_ns, is_dir)
                    VALUES (?,?,?,?,?)
                    """,
                    batch,
                )
                conn.commit()
                updated += len(batch)
        finally:
            conn.close()
    return updated


def query_large_files(
    volume: str | None,
    min_size_bytes: int,
    extensions: list[str] | None = None,
    limit: int = MAX_RESULTS_PAGE,
    offset: int = 0,
) -> list[dict]:
    """
    Query index for files >= min_size_bytes, optionally filtered by volume and extensions.
    Returns list of {path, size_bytes, mtime_ns}.
    """
    ensure_index_schema()
    with _lock:
        conn = _get_connection()
        try:
            if volume:
                sql = "SELECT path, size_bytes, mtime_ns FROM file_index WHERE volume = ? AND is_dir = 0 AND size_bytes >= ?"
                params: list = [volume, min_size_bytes]
            else:
                sql = "SELECT path, size_bytes, mtime_ns FROM file_index WHERE is_dir = 0 AND size_bytes >= ?"
                params = [min_size_bytes]
            if extensions:
                # Match path ending with extension (case-insensitive via LIKE)
                like_parts = " OR ".join("path LIKE ?" for _ in extensions)
                sql += f" AND ({like_parts})"
                for e in extensions:
                    ext = e if e.startswith(".") else "." + e
                    params.append("%" + ext.lower())
            sql += " ORDER BY size_bytes DESC LIMIT ? OFFSET ?"
            params.extend([limit, offset])
            cur = conn.execute(sql, params)
            return [
                {"path": r[0], "size_bytes": r[1], "mtime_ns": r[2]}
                for r in cur.fetchall()
            ]
        finally:
            conn.close()

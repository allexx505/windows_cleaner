"""
Unit tests for index_service: ensure_index_schema, query_large_files (empty),
full_scan_directory with mock path.
"""
import os
import tempfile
import pytest
from backend.services.index_service import (
    ensure_index_schema,
    query_large_files,
    full_scan_directory,
)


def test_ensure_index_schema():
    ensure_index_schema()


def test_query_large_files_empty():
    rows = query_large_files(volume=None, min_size_bytes=1024 * 1024 * 500, limit=10)
    assert isinstance(rows, list)


def test_full_scan_directory_yields(tmp_path):
    (tmp_path / "a.txt").write_bytes(b"x" * 1000)
    (tmp_path / "b.txt").write_bytes(b"y" * 500)
    items = list(
        full_scan_directory(str(tmp_path), min_size_bytes=500, yield_batch=False)
    )
    assert len(items) >= 1
    path, size, mtime_ns, is_dir = items[0]
    assert os.path.isfile(path)
    assert size >= 500
    assert is_dir is False

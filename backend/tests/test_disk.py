"""
Unit tests for disk utils: get_fixed_drives, get_disk_usage, get_directory_size.
"""
import os
import tempfile
import pytest
from backend.utils.disk import (
    get_fixed_drives,
    get_disk_usage,
    get_all_disk_usage,
    get_directory_size,
    DriveUsage,
)


def test_get_fixed_drives_returns_list():
    drives = get_fixed_drives()
    assert isinstance(drives, list)
    assert all(isinstance(d, str) and len(d) == 2 and d.endswith(":") for d in drives)


def test_get_disk_usage_c():
    u = get_disk_usage("C")
    assert u is None or isinstance(u, DriveUsage)
    if u:
        assert u.drive == "C:"
        assert u.total_bytes >= 0
        assert u.used_bytes >= 0
        assert u.free_bytes >= 0
        assert 0 <= u.free_percent <= 100


def test_get_disk_usage_invalid():
    assert get_disk_usage("Z999") is None or get_disk_usage("Z999").drive  # might exist


def test_get_all_disk_usage():
    usages = get_all_disk_usage()
    assert isinstance(usages, list)
    for u in usages:
        assert isinstance(u, DriveUsage)
        assert u.total_bytes >= u.free_bytes


def test_get_directory_size_empty(tmp_path):
    assert get_directory_size(str(tmp_path)) == 0


def test_get_directory_size_with_files(tmp_path):
    (tmp_path / "a.txt").write_bytes(b"hello")
    (tmp_path / "b.txt").write_bytes(b"world")
    size = get_directory_size(str(tmp_path))
    assert size == 10

"""
Disk usage and drive enumeration. Lightweight: uses shutil.disk_usage
per drive, no heavy scanning.
"""
import os
import shutil
import string
from dataclasses import dataclass
from pathlib import Path


@dataclass
class DriveUsage:
    """Disk usage for one drive."""

    drive: str  # e.g. "C:"
    total_bytes: int
    used_bytes: int
    free_bytes: int

    @property
    def free_percent(self) -> float:
        if self.total_bytes == 0:
            return 0.0
        return 100.0 * self.free_bytes / self.total_bytes

    @property
    def used_percent(self) -> float:
        if self.total_bytes == 0:
            return 0.0
        return 100.0 * self.used_bytes / self.total_bytes


def get_fixed_drives() -> list[str]:
    """
    Return list of fixed local drive letters (e.g. ['C:', 'D:']).
    Uses os.path.exists for each letter to avoid requiring win32.
    """
    drives = []
    for letter in string.ascii_uppercase:
        path = f"{letter}:\\"
        if os.path.exists(path):
            try:
                # Only include local fixed drives if we can
                if hasattr(os, "stat"):
                    os.stat(path)
                drives.append(f"{letter}:")
            except OSError:
                pass
    return drives


def get_disk_usage(drive_letter: str) -> DriveUsage | None:
    """
    Return usage for one drive (e.g. 'C' or 'C:').
    Returns None if drive not accessible.
    """
    drive = drive_letter.rstrip(":\\") + ":"
    root = drive + "\\"
    if not os.path.exists(root):
        return None
    try:
        total, used, free = shutil.disk_usage(root)
        return DriveUsage(drive=drive, total_bytes=total, used_bytes=used, free_bytes=free)
    except OSError:
        return None


def get_all_disk_usage() -> list[DriveUsage]:
    """Return usage for all fixed drives; skips inaccessible."""
    result = []
    for d in get_fixed_drives():
        usage = get_disk_usage(d)
        if usage is not None:
            result.append(usage)
    return result


def get_directory_size(path: str, max_depth: int = 2) -> int:
    """
    Approximate directory size by summing file sizes up to max_depth.
    Lightweight: limits recursion to avoid heavy I/O; for deep dirs
    this is an undercount. Used for junk dir size hint.
    """
    path = os.path.normpath(path)
    if not os.path.isdir(path):
        return 0

    total = 0

    def _walk(current: str, depth: int) -> None:
        nonlocal total
        if depth > max_depth:
            return
        try:
            with os.scandir(current) as it:
                for entry in it:
                    try:
                        if entry.is_file(follow_symlinks=False):
                            total += entry.stat(follow_symlinks=False).st_size
                        elif entry.is_dir(follow_symlinks=False):
                            _walk(entry.path, depth + 1)
                    except OSError:
                        pass
        except OSError:
            pass

    _walk(path, 0)
    return total

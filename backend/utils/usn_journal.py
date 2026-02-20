"""
NTFS USN Journal reader for incremental change detection.
Uses pywin32 DeviceIoControl with FSCTL_QUERY_USN_JOURNAL and
FSCTL_READ_USN_JOURNAL. Falls back to no-op on non-NTFS or access errors.
"""
import os
import struct
from ctypes import sizeof
from dataclasses import dataclass
from typing import Iterator

# IOCTL codes from winioctl.h (Windows SDK)
FSCTL_QUERY_USN_JOURNAL = 0x000900F4
FSCTL_READ_USN_JOURNAL = 0x000900BB

# USN record reason flags (partial)
FILE_CREATE = 0x00000100
FILE_DELETE = 0x00000200
FILE_CHANGE = 0x00000400


@dataclass
class UsnRecord:
    """Simplified USN record: path and change reason."""

    path: str
    reason: int
    is_directory: bool


def _open_volume_handle(drive_letter: str):
    """Open volume handle for \\\\.\\X: (requires admin on some systems)."""
    try:
        import win32file
        drive = drive_letter.rstrip(":\\").upper()
        path = f"\\\\.\\{drive}:"
        return win32file.CreateFile(
            path,
            win32file.GENERIC_READ,
            win32file.FILE_SHARE_READ,
            None,
            win32file.OPEN_EXISTING,
            0,
            None,
        )
    except Exception:
        return None


def query_usn_journal(drive_letter: str) -> dict | None:
    """
    Query USN journal info for the volume. Returns dict with
    UsnJournalID, FirstUsn, NextUsn, etc., or None if not available.
    """
    handle = _open_volume_handle(drive_letter)
    if handle is None:
        return None
    try:
        import win32file
        # FSCTL_QUERY_USN_JOURNAL: no input, output is USN_JOURNAL_DATA_V0
        out_buf = win32file.DeviceIoControl(
            handle,
            FSCTL_QUERY_USN_JOURNAL,
            None,
            48,  # sizeof(USN_JOURNAL_DATA_V0)
        )
        if out_buf and len(out_buf) >= 48:
            # UsnJournalID (8), FirstUsn (8), NextUsn (8), LowestValidUsn (8),
            # MaxUsn (8), MaximumSize (4), AllocationDelta (4)
            return {
                "UsnJournalID": struct.unpack("<Q", out_buf[0:8])[0],
                "FirstUsn": struct.unpack("<q", out_buf[8:16])[0],
                "NextUsn": struct.unpack("<q", out_buf[16:24])[0],
                "LowestValidUsn": struct.unpack("<q", out_buf[24:32])[0],
                "MaxUsn": struct.unpack("<q", out_buf[32:40])[0],
            }
    except Exception:
        pass
    finally:
        try:
            import win32file
            win32file.CloseHandle(handle)
        except Exception:
            pass
    return None


def read_usn_journal(
    drive_letter: str,
    start_usn: int = 0,
    max_records: int = 1000,
) -> Iterator[UsnRecord]:
    """
    Read USN journal records from start_usn. Yields UsnRecord.
    If start_usn is 0, starts from the oldest available.
    Stops after max_records to avoid long runs.
    """
    handle = _open_volume_handle(drive_letter)
    if handle is None:
        return
    try:
        import win32file
        # READ_USN_JOURNAL_DATA_V0: 8+8+4+4+4+4 = 32 bytes
        # StartUsn (8), ReasonMask (4), ReturnOnlyOnClose (4),
        # Timeout (8), BytesToWaitFor (4), UsnJournalID (8)
        info = query_usn_journal(drive_letter)
        if not info:
            return
        journal_id = info["UsnJournalID"]
        if start_usn == 0:
            start_usn = info["FirstUsn"]
        # ReasonMask: all reasons
        reason_mask = 0xFFFFFFFF
        in_buf = struct.pack(
            "<qIIQ",
            start_usn,
            reason_mask,
            0,  # ReturnOnlyOnClose
            journal_id,
        )
        # Padding to 32 bytes for READ_USN_JOURNAL_DATA_V0
        in_buf = in_buf + b"\x00" * (32 - len(in_buf))
        if len(in_buf) < 32:
            in_buf = in_buf.ljust(32, b"\x00")
        out_size = 65536
        count = 0
        next_usn = start_usn
        while count < max_records:
            try:
                out_buf = win32file.DeviceIoControl(
                    handle,
                    FSCTL_READ_USN_JOURNAL,
                    in_buf[:32],
                    out_size,
                )
            except Exception:
                break
            if not out_buf or len(out_buf) < 8:
                break
            # First 8 bytes: next USN to use
            next_usn = struct.unpack("<q", out_buf[0:8])[0]
            pos = 8
            while pos + 60 <= len(out_buf) and count < max_records:
                # USN_RECORD_V2/V3: Length (4), then USN (8), FileReferenceNumber (8), etc.
                rec_len = struct.unpack("<I", out_buf[pos : pos + 4])[0]
                if rec_len == 0 or pos + rec_len > len(out_buf):
                    break
                # Reason (4) at offset 8, FileNameLength (2) at 56, FileNameOffset (2) at 58
                reason = struct.unpack("<I", out_buf[pos + 8 : pos + 12])[0]
                name_len = struct.unpack("<H", out_buf[pos + 56 : pos + 58])[0]
                name_offset = struct.unpack("<H", out_buf[pos + 58 : pos + 60])[0]
                if name_offset + name_len <= rec_len:
                    raw_name = out_buf[pos + name_offset : pos + name_offset + name_len].decode(
                        "utf-16-le", errors="replace"
                    )
                    # FileAttributes: 0x10 = DIRECTORY
                    attr = struct.unpack("<I", out_buf[pos + 12 : pos + 16])[0]
                    yield UsnRecord(
                        path=raw_name,
                        reason=reason,
                        is_directory=bool(attr & 0x10),
                    )
                    count += 1
                pos += rec_len
            if next_usn == struct.unpack("<q", out_buf[0:8])[0] and pos >= len(out_buf):
                break
            in_buf = struct.pack("<qIIQ", next_usn, reason_mask, 0, journal_id)
            in_buf = in_buf.ljust(32, b"\x00")
    finally:
        try:
            import win32file
            win32file.CloseHandle(handle)
        except Exception:
            pass


def is_usn_available(drive_letter: str) -> bool:
    """Return True if USN journal can be queried for this drive (NTFS and access)."""
    return query_usn_journal(drive_letter) is not None

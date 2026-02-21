"""
REST API: disk info, config, rules, scan triggers. All under /api.
"""
from typing import Any

from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from backend.core.config import (
    AppSettings,
    load_config,
    save_config,
)
from backend.utils.startup import set_start_with_windows
from backend.core.constants import DEFAULT_PAGE_SIZE, MAX_RESULTS_PAGE
from backend.services.index_service import (
    ensure_index_schema,
    full_scan_directory,
    index_full_scan_volume,
    query_large_files,
)
from backend.utils.disk import get_all_disk_usage, get_disk_usage
from backend.utils.usn_journal import is_usn_available

router = APIRouter(prefix="/api", tags=["api"])


# --- Disk ---


@router.get("/disk/drives")
def api_disk_drives() -> list[dict]:
    """List fixed drives and basic usage."""
    usages = get_all_disk_usage()
    return [
        {
            "drive": u.drive,
            "total_bytes": u.total_bytes,
            "used_bytes": u.used_bytes,
            "free_bytes": u.free_bytes,
            "free_percent": round(u.free_percent, 2),
            "usn_available": is_usn_available(u.drive),
        }
        for u in usages
    ]


@router.get("/disk/usage/{drive}")
def api_disk_usage(drive: str) -> dict:
    """Get usage for one drive (e.g. C or C:)."""
    u = get_disk_usage(drive)
    if u is None:
        raise HTTPException(status_code=404, detail="Drive not found or not accessible")
    return {
        "drive": u.drive,
        "total_bytes": u.total_bytes,
        "used_bytes": u.used_bytes,
        "free_bytes": u.free_bytes,
        "free_percent": round(u.free_percent, 2),
    }


# --- Config ---


@router.get("/config")
def api_config_get() -> dict:
    """Return current app settings (JSON-serializable)."""
    return load_config().model_dump(mode="json")


class ConfigUpdateBody(BaseModel):
    """Partial config update; only provided keys are applied."""

    start_with_windows: bool | None = None
    on_close: str | None = None
    disk_thresholds: list[dict] | None = None
    cleanup_rules: list[dict] | None = None
    notification: dict | None = None


@router.post("/config")
def api_config_update(body: ConfigUpdateBody) -> dict:
    """Update config with provided fields."""
    settings = load_config()
    d = settings.model_dump(mode="json")
    if body.start_with_windows is not None:
        d["start_with_windows"] = body.start_with_windows
    if body.on_close is not None:
        d["on_close"] = body.on_close
    if body.disk_thresholds is not None:
        d["disk_thresholds"] = body.disk_thresholds
    if body.cleanup_rules is not None:
        d["cleanup_rules"] = body.cleanup_rules
    if body.notification is not None:
        d["notification"] = body.notification
    updated = AppSettings.model_validate(d)
    save_config(updated)
    try:
        set_start_with_windows(updated.start_with_windows)
    except Exception:
        pass
    return updated.model_dump(mode="json")


# --- Large files / index ---


@router.get("/scan/large-files")
def api_scan_large_files(
    drive: str | None = None,
    min_size_mb: float = 500,
    extensions: str | None = None,
    limit: int = DEFAULT_PAGE_SIZE,
    offset: int = 0,
) -> dict:
    """
    Query indexed large files. If index empty, returns empty list; caller
    can trigger rebuild via POST /api/scan/rebuild-index.
    """
    if limit <= 0 or limit > MAX_RESULTS_PAGE:
        limit = DEFAULT_PAGE_SIZE
    exts = [e.strip() for e in extensions.split(",")] if extensions else None
    min_bytes = int(min_size_mb * 1024 * 1024)
    vol = drive.rstrip(":") + ":" if drive else None
    rows = query_large_files(
        volume=vol,
        min_size_bytes=min_bytes,
        extensions=exts,
        limit=limit,
        offset=offset,
    )
    return {"items": rows, "limit": limit, "offset": offset}


class RebuildIndexBody(BaseModel):
    drive: str  # e.g. "C:"


@router.post("/scan/rebuild-index")
def api_scan_rebuild_index(body: RebuildIndexBody) -> dict:
    """Trigger full index rebuild for one drive (runs in background; returns immediately)."""
    drive = body.drive.rstrip(":\\") + ":"
    root = drive + "\\"
    import threading

    def run():
        index_full_scan_volume(drive, root)

    t = threading.Thread(target=run, daemon=True)
    t.start()
    return {"status": "started", "drive": drive}


# --- Folder picker ---


@router.get("/pick-folder")
def api_pick_folder(initial_dir: str | None = None) -> dict:
    """
    Open a native folder picker dialog and return selected path.
    Returns empty string if user cancels.
    """
    import threading
    result = {"path": ""}
    event = threading.Event()

    def pick():
        try:
            import tkinter as tk
            from tkinter import filedialog
            root = tk.Tk()
            root.withdraw()
            root.attributes("-topmost", True)
            path = filedialog.askdirectory(
                initialdir=initial_dir or "",
                title="选择文件夹"
            )
            root.destroy()
            result["path"] = path or ""
        except Exception:
            result["path"] = ""
        finally:
            event.set()

    t = threading.Thread(target=pick)
    t.start()
    event.wait(timeout=120)
    return result


# --- Health ---


@router.get("/health")
def api_health() -> dict:
    return {"status": "ok"}

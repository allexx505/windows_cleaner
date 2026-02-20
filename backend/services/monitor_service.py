"""
Monitor: disk threshold check and cleanup rule execution. Runs on a fixed
internal schedule; consults resource_guard before heavy work.
"""
import os
import threading
import time
from typing import Callable

from backend.core.config import load_config
from backend.core.constants import (
    DISK_CHECK_INTERVAL_MINUTES,
    JUNK_SUBPATHS,
    LARGE_FILE_JUNK_SCAN_INTERVAL_HOURS,
)
from backend.services.notification_service import notify_alert
from backend.services.resource_guard import is_under_load, throttle_if_needed
from backend.services.index_service import (
    full_scan_directory,
    index_full_scan_volume,
    query_large_files,
)
from backend.utils.disk import get_all_disk_usage, get_disk_usage, get_directory_size


def check_disk_thresholds() -> None:
    """
    Check all drives against user-configured thresholds; notify if free
    percent is below threshold. Lightweight (only disk_usage).
    """
    if is_under_load():
        return
    cfg = load_config()
    thresholds = getattr(cfg, "disk_thresholds", []) or []
    if not thresholds:
        return
    usages = get_all_disk_usage()
    for u in usages:
        for t in thresholds:
            drive_letter = (getattr(t, "drive_letter", None) or "").strip().upper()
            if drive_letter and not u.drive.upper().startswith(drive_letter.rstrip(":")):
                continue
            alert_below = getattr(t, "free_percent_alert_below", 10)
            if u.free_percent < alert_below:
                notify_alert(
                    "磁盘空间不足",
                    f"{u.drive} 剩余 {u.free_percent:.1f}%，低于 {alert_below}%。请及时清理。",
                )
                return  # One notification per run to avoid spam


def get_junk_dirs() -> list[str]:
    """Return list of junk directory paths (existing only)."""
    dirs = []
    local = os.environ.get("LOCALAPPDATA", "")
    if local:
        for sub in JUNK_SUBPATHS:
            p = os.path.join(local, sub)
            if os.path.isdir(p):
                dirs.append(p)
    for key in ["TEMP", "TMP"]:
        val = os.environ.get(key, "")
        if val and os.path.isdir(val):
            dirs.append(val)
    return dirs


def run_junk_scan() -> tuple[int, int]:
    """
    Sum approximate size of junk dirs (lightweight). Returns (total_bytes, dir_count).
    """
    if is_under_load():
        return 0, 0
    junk = get_junk_dirs()
    total = 0
    for path in junk:
        throttle_if_needed()
        total += get_directory_size(path)
    return total, len(junk)


def run_rule_scan(rule: dict) -> list[dict]:
    """
    Run one cleanup rule: scan target_path and return list of matching files
    {path, size_bytes}. Uses full_scan_directory with batching; respects resource_guard.
    """
    path = (rule.get("target_path") or "").strip()
    if not path or not os.path.isdir(path):
        return []
    rule_type = rule.get("rule_type", "large_file")
    min_mb = float(rule.get("size_mb_min", 500))
    min_bytes = int(min_mb * 1024 * 1024)
    extensions = rule.get("extensions") or []
    if rule_type == "large_file":
        items = list(
            full_scan_directory(path, min_size_bytes=min_bytes, extensions=None, yield_batch=True)
        )
    elif rule_type == "by_extension":
        items = list(
            full_scan_directory(path, min_size_bytes=0, extensions=extensions, yield_batch=True)
        )
    else:
        # junk: treat as size-only hint per dir
        items = []
    return [{"path": p, "size_bytes": s} for (p, s, _, _) in items[:100]]


def run_scheduled_rules() -> None:
    """Run all enabled cleanup rules (scan only; notify or auto-clean per rule)."""
    if is_under_load():
        return
    cfg = load_config()
    rules = getattr(cfg, "cleanup_rules", []) or []
    for rule in rules:
        if not rule.get("enabled", True):
            continue
        throttle_if_needed()
        matches = run_rule_scan(rule)
        if not matches:
            continue
        total_mb = sum(m["size_bytes"] for m in matches) / (1024 * 1024)
        path = rule.get("target_path", "")
        if rule.get("auto_clean"):
            # Optional: move to recycle or delete (plan: suggest recycle)
            notify_alert(
                "清理规则可自动清理",
                f"{path} 下发现 {len(matches)} 个匹配文件，共 {total_mb:.1f} MB。已设为自动清理时可执行清理。",
            )
        else:
            notify_alert(
                "清理提醒",
                f"{path} 下发现 {len(matches)} 个匹配文件，共 {total_mb:.1f} MB。建议清理。",
            )


def start_background_scheduler(on_disk_check: Callable[[], None] | None = None) -> None:
    """
    Start a background thread that runs disk check and (less often) rule/junk
    scans at fixed intervals. Internal intervals only; resource_guard applied.
    """
    last_disk = [0.0]
    last_rules = [0.0]

    def loop() -> None:
        while True:
            try:
                now = time.monotonic()
                # Disk check every DISK_CHECK_INTERVAL_MINUTES
                if (now - last_disk[0]) >= DISK_CHECK_INTERVAL_MINUTES * 60:
                    last_disk[0] = now
                    check_disk_thresholds()
                    if on_disk_check:
                        on_disk_check()
                # Rules + junk every LARGE_FILE_JUNK_SCAN_INTERVAL_HOURS
                if (now - last_rules[0]) >= LARGE_FILE_JUNK_SCAN_INTERVAL_HOURS * 3600:
                    last_rules[0] = now
                    run_scheduled_rules()
                    run_junk_scan()
            except Exception:
                pass
            time.sleep(60)

    t = threading.Thread(target=loop, daemon=True)
    t.start()

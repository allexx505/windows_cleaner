"""
Resource self-monitoring and automatic throttling. Internal thresholds
are not exposed to user config. Scans and scheduler consult this module
to decide whether to sleep, reduce batch size, or defer work.
"""
import threading
import time
from typing import Callable

from backend.core.constants import (
    CPU_PERCENT_THRESHOLD,
    HIGH_LOAD_SLEEP_SECONDS,
    MEMORY_MB_THRESHOLD,
    RESOURCE_CHECK_INTERVAL_SECONDS,
)

_guard_lock = threading.Lock()
_last_check_time = 0.0
_last_cpu_percent: float | None = None
_last_memory_mb: float | None = None
_process: "object | None" = None  # psutil.Process()


def _get_process():
    """Lazy init psutil Process for current process."""
    global _process
    if _process is None:
        try:
            import psutil
            _process = psutil.Process()
        except Exception:
            pass
    return _process


def _sample() -> tuple[float, float]:
    """Return (cpu_percent, memory_mb) for current process."""
    proc = _get_process()
    cpu = 0.0
    mem_mb = 0.0
    if proc is not None:
        try:
            cpu = proc.cpu_percent(interval=None) or 0.0
            mem_mb = (proc.memory_info().rss or 0) / (1024 * 1024)
        except Exception:
            pass
    return cpu, mem_mb


def _cached_sample() -> tuple[float, float]:
    """Sample at most every RESOURCE_CHECK_INTERVAL_SECONDS."""
    global _last_check_time, _last_cpu_percent, _last_memory_mb
    with _guard_lock:
        now = time.monotonic()
        if now - _last_check_time >= RESOURCE_CHECK_INTERVAL_SECONDS:
            _last_cpu_percent, _last_memory_mb = _sample()
            _last_check_time = now
        return (
            _last_cpu_percent if _last_cpu_percent is not None else 0.0,
            _last_memory_mb if _last_memory_mb is not None else 0.0,
        )


def is_under_load() -> bool:
    """
    True if we should throttle: process CPU or memory exceeds internal
    thresholds. Call before starting or during heavy work.
    """
    cpu, mem_mb = _cached_sample()
    if cpu >= CPU_PERCENT_THRESHOLD:
        return True
    if mem_mb >= MEMORY_MB_THRESHOLD:
        return True
    return False


def throttle_if_needed() -> None:
    """
    If under load, sleep for HIGH_LOAD_SLEEP_SECONDS. Call in scan loops
    to automatically back off.
    """
    if is_under_load():
        time.sleep(HIGH_LOAD_SLEEP_SECONDS)


def run_if_idle(fn: Callable[[], None], max_wait_sec: float = 60.0) -> bool:
    """
    Run fn when not under load, checking every few seconds. Returns True
    if fn was run, False if max_wait_sec elapsed while under load.
    """
    deadline = time.monotonic() + max_wait_sec
    while time.monotonic() < deadline:
        if not is_under_load():
            fn()
            return True
        time.sleep(RESOURCE_CHECK_INTERVAL_SECONDS)
    return False

"""
Configuration load/save. User-facing options only; resource-related
intervals and limits stay in constants.py and resource_guard.
"""
import json
import os
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field

from backend.core.constants import CONFIG_DIR, CONFIG_FILE


class DiskThresholdConfig(BaseModel):
    """Per-drive or global disk space alert threshold."""

    drive_letter: str | None = None  # None = apply to all
    free_percent_alert_below: float = Field(ge=0, le=100, default=10.0)


class CleanupRuleConfig(BaseModel):
    """Single cleanup rule: path, type, schedule, auto or notify-only."""

    id: str = ""
    enabled: bool = True
    target_path: str = ""
    rule_type: str = "large_file"  # large_file | by_extension | junk
    size_mb_min: float = 500.0  # for large_file
    extensions: list[str] = Field(default_factory=lambda: [".mp4", ".avi"])  # for by_extension
    cron_expr: str = "0 3 * * *"  # default 3:00 daily
    auto_clean: bool = False  # False = notify only


class NotificationConfig(BaseModel):
    """Notification channels."""

    use_windows_toast: bool = True
    email_enabled: bool = False
    smtp_host: str = ""
    smtp_port: int = 465
    smtp_user: str = ""
    smtp_password: str = ""
    smtp_use_tls: bool = True
    notify_email_to: str = ""


class AppSettings(BaseModel):
    """All user-facing app settings."""

    # Startup & UI
    start_with_windows: bool = False
    on_close: str = "minimize_to_tray"  # minimize_to_tray | quit

    # Disk alerts
    disk_thresholds: list[DiskThresholdConfig] = Field(default_factory=list)

    # Cleanup rules
    cleanup_rules: list[CleanupRuleConfig] = Field(default_factory=list)

    # Notifications
    notification: NotificationConfig = Field(default_factory=NotificationConfig)

    def model_dump_json(self, **kwargs: Any) -> str:
        return self.model_dump(mode="json", **kwargs)


def ensure_config_dir() -> None:
    """Create config directory if it does not exist."""
    Path(CONFIG_DIR).mkdir(parents=True, exist_ok=True)


def load_config() -> AppSettings:
    """Load config from JSON file; return defaults if missing or invalid."""
    ensure_config_dir()
    if not os.path.isfile(CONFIG_FILE):
        return AppSettings()
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        return AppSettings.model_validate(data)
    except Exception:
        return AppSettings()


def save_config(settings: AppSettings) -> None:
    """Persist settings to JSON file."""
    ensure_config_dir()
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        f.write(settings.model_dump_json(indent=2))


def get_config_path() -> str:
    """Return path to config file (for API)."""
    return CONFIG_FILE

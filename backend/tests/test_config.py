"""
Unit tests for config load/save and validation.
"""
import json
import os
import tempfile
import pytest
from backend.core.config import (
    AppSettings,
    DiskThresholdConfig,
    CleanupRuleConfig,
    load_config,
    save_config,
)
from backend.core import constants


def test_app_settings_defaults():
    s = AppSettings()
    assert s.on_close in ("minimize_to_tray", "quit")
    assert isinstance(s.cleanup_rules, list)
    assert isinstance(s.disk_thresholds, list)


def test_disk_threshold_validation():
    t = DiskThresholdConfig(drive_letter="C", free_percent_alert_below=10)
    assert t.free_percent_alert_below == 10
    with pytest.raises(Exception):
        DiskThresholdConfig(free_percent_alert_below=150)


def test_cleanup_rule_validation():
    r = CleanupRuleConfig(target_path="C:\\Temp", rule_type="large_file", size_mb_min=500)
    assert r.size_mb_min == 500
    assert r.rule_type == "large_file"


def test_config_roundtrip(monkeypatch):
    with tempfile.TemporaryDirectory() as d:
        config_file = os.path.join(d, "config.json")
        monkeypatch.setattr(constants, "CONFIG_DIR", d)
        monkeypatch.setattr(constants, "CONFIG_FILE", config_file)
        # config module imports these at load time; patch there too
        import backend.core.config as config_mod
        monkeypatch.setattr(config_mod, "CONFIG_DIR", d)
        monkeypatch.setattr(config_mod, "CONFIG_FILE", config_file)
        s = AppSettings(start_with_windows=True, on_close="quit")
        save_config(s)
        loaded = load_config()
        assert loaded.start_with_windows is True
        assert loaded.on_close == "quit"

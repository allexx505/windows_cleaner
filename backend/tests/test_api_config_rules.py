"""
API tests: config roundtrip with disk_thresholds and cleanup_rules.
Uses FastAPI TestClient; config is written to a temp dir via monkeypatch.
"""
import os
import tempfile
import pytest
from fastapi.testclient import TestClient

from backend.main import app
from backend.core import constants
import backend.core.config as config_mod


@pytest.fixture
def temp_config_dir(monkeypatch):
    """Point config to a temp directory for the test."""
    with tempfile.TemporaryDirectory() as d:
        config_file = os.path.join(d, "config.json")
        monkeypatch.setattr(constants, "CONFIG_DIR", d)
        monkeypatch.setattr(constants, "CONFIG_FILE", config_file)
        monkeypatch.setattr(config_mod, "CONFIG_DIR", d)
        monkeypatch.setattr(config_mod, "CONFIG_FILE", config_file)
        yield d


def test_api_config_post_get_disk_thresholds_and_cleanup_rules(temp_config_dir):
    """POST /api/config with disk_thresholds and cleanup_rules, then GET and assert roundtrip."""
    client = TestClient(app)
    disk_thresholds = [
        {"drive_letter": "C", "free_percent_alert_below": 15},
    ]
    cleanup_rules = [
        {
            "id": "r1",
            "enabled": True,
            "target_path": "C:\\Temp",
            "rule_type": "large_file",
            "size_mb_min": 100.0,
            "auto_clean": False,
        },
    ]
    body = {
        "disk_thresholds": disk_thresholds,
        "cleanup_rules": cleanup_rules,
    }
    r = client.post("/api/config", json=body)
    assert r.status_code == 200

    get_r = client.get("/api/config")
    assert get_r.status_code == 200
    data = get_r.json()
    assert "disk_thresholds" in data
    assert "cleanup_rules" in data
    # Model may add default fields; check key fields only
    assert len(data["disk_thresholds"]) >= 1
    assert data["disk_thresholds"][0]["drive_letter"] == "C"
    assert data["disk_thresholds"][0]["free_percent_alert_below"] == 15
    assert len(data["cleanup_rules"]) >= 1
    assert data["cleanup_rules"][0]["id"] == "r1"
    assert data["cleanup_rules"][0]["target_path"] == "C:\\Temp"
    assert data["cleanup_rules"][0]["rule_type"] == "large_file"
    assert data["cleanup_rules"][0]["size_mb_min"] == 100.0
    assert data["cleanup_rules"][0]["auto_clean"] is False

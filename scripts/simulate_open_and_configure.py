"""
Simulate "open app -> configure disk cleanup rule -> verify".
Run with the API already up (e.g. python run.py --no-tray in another terminal).
From project root: python scripts/simulate_open_and_configure.py
"""
import sys
import time

try:
    import httpx
except ImportError:
    print("Need httpx. pip install httpx")
    sys.exit(1)

BASE = "http://127.0.0.1:8765"
HEALTH_URL = f"{BASE}/api/health"
CONFIG_URL = f"{BASE}/api/config"
TIMEOUT_WAIT = 15.0
POLL_INTERVAL = 0.5


def main() -> None:
    # 1) Wait for server
    deadline = time.monotonic() + TIMEOUT_WAIT
    while time.monotonic() < deadline:
        try:
            r = httpx.get(HEALTH_URL, timeout=2.0)
            if r.status_code == 200:
                break
        except Exception:
            pass
        time.sleep(POLL_INTERVAL)
    else:
        print("Service not ready. Start it first: python run.py --no-tray")
        sys.exit(1)

    # 2) POST config: one disk threshold, one cleanup rule
    disk_thresholds = [{"drive_letter": "C", "free_percent_alert_below": 15}]
    cleanup_rules = [
        {
            "id": "sim_r1",
            "enabled": True,
            "target_path": "C:\\Temp",
            "rule_type": "large_file",
            "size_mb_min": 100.0,
            "auto_clean": False,
        }
    ]
    body = {"disk_thresholds": disk_thresholds, "cleanup_rules": cleanup_rules}
    r = httpx.post(CONFIG_URL, json=body, timeout=5.0)
    if r.status_code != 200:
        print("POST /api/config failed:", r.status_code, r.text)
        sys.exit(1)

    # 3) GET config and assert key fields match (model may add defaults)
    r = httpx.get(CONFIG_URL, timeout=5.0)
    if r.status_code != 200:
        print("GET /api/config failed:", r.status_code)
        sys.exit(1)
    data = r.json()
    # disk_thresholds: check drive_letter and free_percent_alert_below
    got_thresh = data.get("disk_thresholds", [])
    if len(got_thresh) < 1:
        print("disk_thresholds missing")
        sys.exit(1)
    t = got_thresh[0]
    if t.get("drive_letter") != "C" or t.get("free_percent_alert_below") != 15:
        print("disk_threshold mismatch:", t)
        sys.exit(1)
    # cleanup_rules: check id, target_path, rule_type, size_mb_min, auto_clean
    got_rules = data.get("cleanup_rules", [])
    if len(got_rules) < 1:
        print("cleanup_rules missing")
        sys.exit(1)
    cr = got_rules[0]
    if cr.get("id") != "sim_r1" or cr.get("target_path") != "C:\\Temp":
        print("cleanup_rule id/path mismatch:", cr)
        sys.exit(1)
    if cr.get("rule_type") != "large_file" or cr.get("size_mb_min") != 100.0:
        print("cleanup_rule type/size mismatch:", cr)
        sys.exit(1)
    if cr.get("auto_clean") is not False:
        print("cleanup_rule auto_clean mismatch:", cr)
        sys.exit(1)

    print("OK: simulated open -> configure rule -> verify; config persisted.")


if __name__ == "__main__":
    main()

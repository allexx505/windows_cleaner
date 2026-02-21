"""全面功能测试脚本"""
import requests
import time
import subprocess
import sys
import os

BASE_URL = "http://127.0.0.1:8765"

def test_health():
    r = requests.get(f"{BASE_URL}/api/health", timeout=5)
    assert r.status_code == 200
    assert r.json()["status"] == "ok"
    print("[OK] Health check")

def test_disk_drives():
    r = requests.get(f"{BASE_URL}/api/disk/drives", timeout=10)
    assert r.status_code == 200
    data = r.json()
    assert isinstance(data, list)
    assert len(data) > 0
    print(f"[OK] Disk drives: {len(data)} drives found")
    for d in data:
        print(f"     {d['drive']}: {d['free_percent']:.1f}% free")

def test_disk_usage():
    r = requests.get(f"{BASE_URL}/api/disk/usage/C", timeout=5)
    assert r.status_code == 200
    data = r.json()
    assert "drive" in data
    assert "total_bytes" in data
    print(f"[OK] Disk usage C: {data['free_bytes']/1024/1024/1024:.2f} GB free")

def test_config_get():
    r = requests.get(f"{BASE_URL}/api/config", timeout=5)
    assert r.status_code == 200
    data = r.json()
    assert "start_with_windows" in data
    assert "cleanup_rules" in data
    print(f"[OK] Config get: {len(data.get('cleanup_rules', []))} rules")

def test_config_update():
    # First get current
    r = requests.get(f"{BASE_URL}/api/config", timeout=5)
    original = r.json()
    
    # Update and restore
    r = requests.post(f"{BASE_URL}/api/config", json={"on_close": "minimize"}, timeout=5)
    assert r.status_code == 200
    
    # Restore
    r = requests.post(f"{BASE_URL}/api/config", json={"on_close": original.get("on_close", "minimize")}, timeout=5)
    assert r.status_code == 200
    print("[OK] Config update")

def test_large_files():
    r = requests.get(f"{BASE_URL}/api/scan/large-files", params={"min_size_mb": 500, "limit": 10}, timeout=10)
    assert r.status_code == 200
    data = r.json()
    assert "items" in data
    print(f"[OK] Large files: {len(data['items'])} files >= 500MB")

def test_rebuild_index():
    r = requests.post(f"{BASE_URL}/api/scan/rebuild-index", json={"drive": "C:"}, timeout=5)
    assert r.status_code == 200
    data = r.json()
    assert data.get("status") == "started"
    print("[OK] Rebuild index triggered")

def test_frontend_served():
    r = requests.get(f"{BASE_URL}/", timeout=5)
    assert r.status_code == 200
    assert "<!DOCTYPE html>" in r.text or "<html" in r.text
    print("[OK] Frontend served")

def main():
    print("=" * 50)
    print("Windows Cleaner 全功能测试")
    print("=" * 50)
    
    tests = [
        test_health,
        test_disk_drives,
        test_disk_usage,
        test_config_get,
        test_config_update,
        test_large_files,
        test_rebuild_index,
        test_frontend_served,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            test()
            passed += 1
        except requests.exceptions.ConnectionError:
            print(f"[FAIL] {test.__name__}: Server not running")
            failed += 1
        except AssertionError as e:
            print(f"[FAIL] {test.__name__}: {e}")
            failed += 1
        except Exception as e:
            print(f"[FAIL] {test.__name__}: {type(e).__name__}: {e}")
            failed += 1
    
    print("=" * 50)
    print(f"Results: {passed} passed, {failed} failed")
    print("=" * 50)
    return failed == 0

if __name__ == "__main__":
    sys.exit(0 if main() else 1)

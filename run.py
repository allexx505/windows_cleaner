"""
Launcher for Windows Cleaner. Used as PyInstaller entry so that the whole
backend package is collected. From project root: python run.py [--gui]
"""
import os
import sys
import time

ROOT = os.path.abspath(os.path.dirname(__file__))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

# Delegate to backend.main and tray (same as: python -m backend.main)
from backend.main import run_server, _disk_check_callback
from backend.services.tray_service import run_tray
from backend.main import app  # noqa: F401 - for PyInstaller to pull in app


def _kill_old_instances(port: int) -> None:
    """
    启动前结束占用本程序端口或同名 exe 的旧进程，避免残留导致无法启动。
    先结束占用 port 的进程，再（若为打包 exe）结束其他 WindowsCleaner.exe。
    """
    current_pid = os.getpid()
    killed_any = False
    try:
        import psutil
    except ImportError:
        return
    # 1) 结束占用本程序端口的进程（必为旧实例）
    try:
        for conn in psutil.net_connections(kind="inet"):
            if conn.status != "LISTEN" or conn.laddr.port != port:
                continue
            pid = conn.pid
            if pid is None or pid == current_pid:
                continue
            try:
                p = psutil.Process(pid)
                p.terminate()
                p.wait(timeout=3)
                killed_any = True
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.TimeoutExpired):
                try:
                    p.kill()
                except Exception:
                    pass
    except Exception:
        pass
    # 2) 若为打包 exe，再结束其他同名进程（避免托盘/子进程残留）
    if getattr(sys, "frozen", False):
        try:
            for p in psutil.process_iter(["pid", "name"]):
                if p.info["pid"] == current_pid:
                    continue
                name = (p.info.get("name") or "").lower()
                if "windowscleaner" in name or (name.endswith(".exe") and "windows cleaner" in name):
                    try:
                        p.terminate()
                        p.wait(timeout=2)
                        killed_any = True
                    except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.TimeoutExpired):
                        try:
                            p.kill()
                        except Exception:
                            pass
        except Exception:
            pass
    if killed_any:
        time.sleep(1.5)

def _wait_for_server(port: int, timeout_sec: float = 15.0, interval: float = 0.5) -> bool:
    """等待本地服务就绪，返回 True 表示已就绪。"""
    import socket
    import time
    import urllib.request
    url = f"http://127.0.0.1:{port}/api/health"
    deadline = time.monotonic() + timeout_sec
    while time.monotonic() < deadline:
        try:
            req = urllib.request.Request(url)
            urllib.request.urlopen(req, timeout=2)
            return True
        except (OSError, urllib.error.URLError, socket.timeout):
            time.sleep(interval)
    return False


def _open_main_window(port: int) -> None:
    """打开主界面：先等待服务就绪，再优先用 PyWebView，否则用默认浏览器。"""
    import threading
    if not _wait_for_server(port):
        return  # 服务未启动则不打开，避免显示“无法访问”
    url = f"http://127.0.0.1:{port}"
    try:
        import webview
        def _show() -> None:
            webview.create_window("Windows 文件清理工具", url, width=900, height=700)
            webview.start()
        threading.Thread(target=_show, daemon=True).start()
    except ImportError:
        import webbrowser
        webbrowser.open(url)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--gui", action="store_true", help="Start with tray")
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument("--no-tray", action="store_true")
    args = parser.parse_args()
    port = args.port
    # 启动前强制结束占用端口或同名 exe 的旧进程
    _kill_old_instances(port)
    # 双击 exe 时无参数，默认以托盘方式启动并显示界面
    if getattr(sys, "frozen", False) and len(sys.argv) <= 1:
        args.gui = True
    if args.gui and not args.no_tray:
        import threading
        import time
        def run_api() -> None:
            run_server(port=port)
        t = threading.Thread(target=run_api, daemon=True)
        t.start()
        time.sleep(1)
        _disk_check_callback()
        # 约 2 秒后自动弹出主界面，避免用户以为没启动
        threading.Timer(2.0, _open_main_window, args=(port,)).start()
        run_tray(port=port)
    else:
        run_server(port=port)

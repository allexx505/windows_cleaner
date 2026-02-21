"""
Launcher for Windows Cleaner. Used as PyInstaller entry so that the whole
backend package is collected. From project root: python run.py [--gui]
"""
import os
import sys
import time
import traceback

ROOT = os.path.abspath(os.path.dirname(__file__))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

# Bootstrap log path (same as backend/core/constants CONFIG_DIR + logs); no backend import
def _bootstrap_log_path() -> str:
    base = os.path.join(os.environ.get("APPDATA", ""), "WindowsCleaner")
    return os.path.join(base, "logs", "windows_cleaner.log")


def _bootstrap_log(msg: str, exc_text: str | None = None) -> None:
    """Append one line (and optional traceback) to bootstrap log file. Stdlib only."""
    path = _bootstrap_log_path()
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "a", encoding="utf-8") as f:
            f.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} {msg}\n")
            if exc_text:
                f.write(exc_text)
                f.write("\n")
            f.flush()
    except OSError:
        pass


# Lazy imports for backend - will be done inside main to enable logging before import errors
run_server = None
_disk_check_callback = None
run_tray = None
app = None


def _import_backend() -> None:
    """Import backend modules. Call after bootstrap log is set up."""
    global run_server, _disk_check_callback, run_tray, app
    from backend.main import run_server as _run_server, _disk_check_callback as _disk_cb
    from backend.services.tray_service import run_tray as _run_tray
    from backend.main import app as _app
    run_server = _run_server
    _disk_check_callback = _disk_cb
    run_tray = _run_tray
    app = _app


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


def _open_main_window_webview(port: int, keep_tray_after_close: bool = True) -> None:
    """使用 pywebview 打开主界面（需在主线程调用）。
    
    Args:
        keep_tray_after_close: 如果为 True，关闭窗口后保持托盘运行
    """
    if not _wait_for_server(port):
        _bootstrap_log("server not ready, skip webview")
        return
    url = f"http://127.0.0.1:{port}"
    try:
        import webview
        _bootstrap_log("starting webview")
        window = webview.create_window(
            "Windows 文件清理工具",
            url,
            width=1000,
            height=700,
            min_size=(800, 600),
        )
        webview.start()
        _bootstrap_log("webview closed by user")
        if keep_tray_after_close:
            _bootstrap_log("keeping tray running after webview close")
            _keep_running()
    except ImportError:
        _bootstrap_log("webview not available, using browser")
        import webbrowser
        webbrowser.open(url)
        _keep_running()
    except Exception:
        _bootstrap_log("webview failed", traceback.format_exc())
        import webbrowser
        webbrowser.open(url)
        _keep_running()


def _keep_running() -> None:
    """保持进程运行（浏览器模式下使用）。"""
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        pass


def _open_main_window_browser(port: int) -> None:
    """使用默认浏览器打开主界面。"""
    if not _wait_for_server(port):
        return
    url = f"http://127.0.0.1:{port}"
    import webbrowser
    webbrowser.open(url)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--gui", action="store_true", help="Start with tray")
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument("--no-tray", action="store_true")
    parser.add_argument("--browser", action="store_true", help="Use browser instead of webview")
    args = parser.parse_args()
    port = args.port
    frozen = getattr(sys, "frozen", False)
    gui = getattr(args, "gui", False)
    _bootstrap_log(f"bootstrap started frozen={frozen} gui={gui} port={port}")

    log_path = _bootstrap_log_path()
    try:
        # Import backend modules first (enables logging of import errors)
        _bootstrap_log("importing backend")
        _import_backend()
        _bootstrap_log("backend imported")
        # 启动前强制结束占用端口或同名 exe 的旧进程
        _kill_old_instances(port)
        _bootstrap_log("kill_old done")
        # 双击 exe 时无参数，默认以托盘方式启动并显示界面
        if frozen and len(sys.argv) <= 1:
            args.gui = True
            gui = True
        if args.gui and not args.no_tray:
            _bootstrap_log("gui mode")
            # 尽早初始化日志，便于主线程与服务器线程统一写日志
            try:
                from backend.core.logging_config import setup_logging
                setup_logging()
            except Exception:
                _bootstrap_log("setup_logging failed", traceback.format_exc())
                raise
            import threading

            def run_api() -> None:
                try:
                    run_server(port=port)
                except Exception:
                    _bootstrap_log("server thread failed", traceback.format_exc())
                    raise

            def run_tray_thread() -> None:
                try:
                    run_tray(port=port, bootstrap_log_path=log_path)
                except Exception:
                    _bootstrap_log("tray thread failed", traceback.format_exc())

            # 启动 API 服务器线程
            t_api = threading.Thread(target=run_api, daemon=True)
            t_api.start()
            _bootstrap_log("server thread started")

            # 启动托盘线程
            t_tray = threading.Thread(target=run_tray_thread, daemon=True)
            t_tray.start()
            _bootstrap_log("tray thread started")

            time.sleep(1)
            _disk_check_callback()

            # 主线程运行 webview（webview 必须在主线程）
            _bootstrap_log("about to open webview on main thread")
            if args.browser:
                _open_main_window_browser(port)
                _keep_running()
            else:
                _open_main_window_webview(port)
        else:
            try:
                from backend.core.logging_config import setup_logging
                setup_logging()
            except Exception:
                _bootstrap_log("setup_logging failed", traceback.format_exc())
                raise
            run_server(port=port)
    except Exception:
        _bootstrap_log("main thread failed", traceback.format_exc())
        try:
            import ctypes
            if sys.platform == "win32":
                ctypes.windll.user32.MessageBoxW(
                    None,
                    f"启动失败，请查看日志：\n{log_path}",
                    "Windows 文件清理工具",
                    0x10,
                )
        except Exception:
            pass
        sys.exit(1)

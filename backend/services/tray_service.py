"""
System tray icon: tooltip with disk summary, menu (open, exit), and
optional PyWebView window. Close behavior (minimize to tray vs quit) from config.
"""
import os
import sys
import threading
import webbrowser
from typing import Callable

# Cache for tooltip text (updated by monitor callback)
_tooltip_lines: list[str] = []
_tooltip_lock = threading.Lock()
_current_icon: "object | None" = None  # pystray.Icon ref for updating title


def _get_icon_path() -> str | None:
    """Get the path to app_icon.ico, handling both dev and frozen modes."""
    if getattr(sys, "frozen", False):
        # PyInstaller: look in _MEIPASS (temp dir) or beside exe
        base = getattr(sys, "_MEIPASS", os.path.dirname(sys.executable))
        candidates = [
            os.path.join(base, "assets", "app_icon.ico"),
            os.path.join(base, "app_icon.ico"),
            os.path.join(os.path.dirname(sys.executable), "assets", "app_icon.ico"),
        ]
    else:
        # Dev mode: project root / assets
        root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        candidates = [
            os.path.join(root, "assets", "app_icon.ico"),
        ]
    for p in candidates:
        if os.path.isfile(p):
            return p
    return None


def set_tooltip_lines(lines: list[str]) -> None:
    """Update tooltip content (e.g. from disk check callback)."""
    with _tooltip_lock:
        _tooltip_lines.clear()
        _tooltip_lines.extend(lines)


def get_tooltip_text() -> str:
    """Current tooltip string."""
    with _tooltip_lock:
        if not _tooltip_lines:
            return "Windows Cleaner"
        return "\n".join(_tooltip_lines)


def _write_tray_error(msg: str, exc_text: str | None, bootstrap_log_path: str | None) -> None:
    """Write tray error to logger or bootstrap log file."""
    if bootstrap_log_path:
        try:
            import os
            import time
            os.makedirs(os.path.dirname(bootstrap_log_path), exist_ok=True)
            with open(bootstrap_log_path, "a", encoding="utf-8") as f:
                f.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} tray: {msg}\n")
                if exc_text:
                    f.write(exc_text)
                    f.write("\n")
                f.flush()
        except OSError:
            pass
    try:
        from backend.core.logging_config import get_logger
        if exc_text:
            get_logger().error("%s\n%s", msg, exc_text)
        else:
            get_logger().error("%s", msg)
    except Exception:
        pass


def run_tray(
    port: int = 8765,
    on_open: Callable[[], None] | None = None,
    on_quit: Callable[[], None] | None = None,
    bootstrap_log_path: str | None = None,
) -> None:
    """
    Run system tray icon (blocking). Menu: Open -> open browser or call on_open;
    Quit -> call on_quit and stop. Tooltip shows disk summary.
    """
    try:
        import pystray
        from PIL import Image
    except ImportError as e:
        _write_tray_error(
            "ImportError (pystray/PIL missing)",
            __import__("traceback").format_exc(),
            bootstrap_log_path,
        )
        return

    url = f"http://127.0.0.1:{port}"

    def open_app(*args: object) -> None:
        if on_open:
            on_open()
        else:
            # Prefer PyWebView if available; else browser
            try:
                import webview
                def show() -> None:
                    w = webview.create_window("Windows 文件清理工具", url, width=900, height=700)
                    webview.start()
                threading.Thread(target=show, daemon=True).start()
            except ImportError:
                webbrowser.open(url)

    def quit_app(*args: object) -> None:
        if on_quit:
            on_quit()
        icon.stop()

    def make_menu() -> pystray.Menu:
        return pystray.Menu(
            pystray.MenuItem("打开", open_app, default=True),
            pystray.MenuItem("退出", quit_app),
        )

    # Load icon from file, fallback to simple colored square
    img = None
    icon_path = _get_icon_path()
    if icon_path:
        try:
            img = Image.open(icon_path)
            img = img.resize((64, 64), Image.Resampling.LANCZOS)
        except Exception:
            img = None
    if img is None:
        try:
            img = Image.new("RGBA", (64, 64), (72, 130, 206, 255))
        except Exception:
            img = None

    global _current_icon
    try:
        icon = pystray.Icon(
            "windows_cleaner",
            img or Image.new("RGB", (64, 64), (72, 130, 206)),
            get_tooltip_text(),
            make_menu(),
        )
        _current_icon = icon
        # Refresh tooltip periodically
        def tick() -> None:
            import time
            while getattr(icon, "visible", True):
                try:
                    icon.title = get_tooltip_text()
                except Exception:
                    pass
                time.sleep(30)

        threading.Thread(target=tick, daemon=True).start()
        icon.run()
    except Exception:
        _write_tray_error(
            "tray icon run failed",
            __import__("traceback").format_exc(),
            bootstrap_log_path,
        )
        raise
    finally:
        _current_icon = None


def run_webview(port: int = 8765) -> None:
    """Open PyWebView window loading local URL (non-blocking in thread)."""
    try:
        import webview
        url = f"http://127.0.0.1:{port}"
        webview.create_window("Windows 文件清理工具", url, width=900, height=700)
        webview.start()
    except Exception:
        pass

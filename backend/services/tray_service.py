"""
System tray icon: tooltip with disk summary, menu (open, exit), and
optional PyWebView window. Close behavior (minimize to tray vs quit) from config.
"""
import threading
import webbrowser
from typing import Callable

# Cache for tooltip text (updated by monitor callback)
_tooltip_lines: list[str] = []
_tooltip_lock = threading.Lock()
_current_icon: "object | None" = None  # pystray.Icon ref for updating title


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


def run_tray(
    port: int = 8765,
    on_open: Callable[[], None] | None = None,
    on_quit: Callable[[], None] | None = None,
) -> None:
    """
    Run system tray icon (blocking). Menu: Open -> open browser or call on_open;
    Quit -> call on_quit and stop. Tooltip shows disk summary.
    """
    try:
        import pystray
        from PIL import Image
    except ImportError:
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

    # Simple 16x16 icon (single color square as fallback)
    try:
        img = Image.new("RGBA", (16, 16), (72, 130, 206, 255))
    except Exception:
        img = None

    global _current_icon
    icon = pystray.Icon(
        "windows_cleaner",
        img or Image.new("RGB", (16, 16), (72, 130, 206)),
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

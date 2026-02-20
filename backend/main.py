"""
Application entry: FastAPI app, static files for Vue SPA, and (when run as GUI)
tray + PyWebView. Run as: python -m backend.main
For GUI: python -m backend.main --gui
"""
import argparse
import os
import sys

# Project root and frontend dist: when frozen (PyInstaller), use _MEIPASS
if getattr(sys, "frozen", False):
    _ROOT = getattr(sys, "_MEIPASS", os.path.dirname(sys.executable))
else:
    _ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from backend.api.routes import router as api_router
from backend.core.constants import APP_NAME, APP_VERSION

app = FastAPI(title=APP_NAME, version=APP_VERSION)
app.include_router(api_router)

# Mount Vue SPA dist when present (packaged: frontend/dist added via PyInstaller datas)
_DIST = os.path.join(_ROOT, "frontend", "dist")
if not os.path.isdir(_DIST) and getattr(sys, "frozen", False):
    _DIST = os.path.join(_ROOT, "dist")  # fallback if bundled as "dist"
if os.path.isdir(_DIST):
    app.mount("/assets", StaticFiles(directory=os.path.join(_DIST, "assets")), name="assets")

    @app.get("/")
    def index():
        from fastapi.responses import FileResponse
        index_path = os.path.join(_DIST, "index.html")
        if os.path.isfile(index_path):
            return FileResponse(index_path)
        return {"message": "Vue SPA not built; run npm run build in frontend/"}

    @app.get("/{path:path}")
    def catch_all(path: str):
        from fastapi.responses import FileResponse
        p = os.path.join(_DIST, path)
        if os.path.isfile(p):
            return FileResponse(p)
        index_path = os.path.join(_DIST, "index.html")
        if os.path.isfile(index_path):
            return FileResponse(index_path)
        return {"message": "Not found"}
else:
    @app.get("/")
    def index():
        return {
            "message": "Windows Cleaner API",
            "docs": "/docs",
            "api": "/api",
        }


def _disk_check_callback() -> None:
    """Update tray tooltip with disk summary and junk size."""
    try:
        from backend.utils.disk import get_all_disk_usage
        from backend.services.monitor_service import run_junk_scan
        from backend.services.tray_service import set_tooltip_lines
        usages = get_all_disk_usage()
        junk_bytes, junk_count = run_junk_scan()
        lines = [
            f"{u.drive} 剩余 {u.free_percent:.1f}% ({u.free_bytes // (1024**3)} GB)"
            for u in usages
        ]
        if junk_count:
            lines.append(f"垃圾目录约 {junk_bytes // (1024**2)} MB")
        set_tooltip_lines(lines)
    except Exception as e:
        try:
            from backend.core.logging_config import get_logger
            get_logger().debug("托盘摘要更新失败: %s", e, exc_info=True)
        except Exception:
            pass


def run_server(host: str = "127.0.0.1", port: int = 8765) -> None:
    """Run uvicorn server (blocking). Starts background monitor scheduler."""
    # When running as packaged GUI (no console), stdout/stderr can be None; uvicorn's
    # default logging formatter calls stream.isatty() and raises. Use safe streams.
    if sys.stdout is None or not getattr(sys.stdout, "isatty", None):
        sys.stdout = open(os.devnull, "w")
    if sys.stderr is None or not getattr(sys.stderr, "isatty", None):
        sys.stderr = open(os.devnull, "w")

    # 本地日志：写入配置目录下 logs/windows_cleaner.log，便于排查问题
    from backend.core.logging_config import setup_logging, get_logger
    log_path = setup_logging()
    logger = get_logger()
    if log_path:
        logger.info("日志文件: %s", log_path)
    logger.info("启动 %s v%s，监听 %s:%s", APP_NAME, APP_VERSION, host, port)

    # Use a simple log config that does not depend on TTY (avoids uvicorn "default" formatter)
    log_config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "default": {"format": "%(levelname)s: %(message)s"},
            "access": {"format": "%(levelname)s: %(message)s"},
        },
        "handlers": {
            "default": {
                "class": "logging.StreamHandler",
                "stream": "ext://sys.stderr",
                "formatter": "default",
            },
            "access": {
                "class": "logging.StreamHandler",
                "stream": "ext://sys.stderr",
                "formatter": "access",
            },
        },
        "loggers": {
            "uvicorn": {"handlers": ["default"], "level": "INFO"},
            "uvicorn.error": {"handlers": ["default"], "level": "INFO"},
            "uvicorn.access": {"handlers": ["access"], "level": "INFO", "propagate": False},
        },
    }
    from backend.services.monitor_service import start_background_scheduler
    start_background_scheduler(on_disk_check=_disk_check_callback)
    logger.info("后台监控调度已启动")
    import uvicorn
    uvicorn.run(app, host=host, port=port, log_level="info", log_config=log_config)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--gui", action="store_true", help="Start with tray and optional PyWebView")
    parser.add_argument("--port", type=int, default=8765, help="HTTP port")
    parser.add_argument("--no-tray", action="store_true", help="With --gui: do not show tray")
    args = parser.parse_args()
    port = args.port
    if args.gui and not args.no_tray:
        # Run server in thread, tray in main thread (tray blocks)
        import threading
        def run_api() -> None:
            run_server(port=port)
        t = threading.Thread(target=run_api, daemon=True)
        t.start()
        # Give server time to bind
        import time
        time.sleep(1)
        from backend.services.tray_service import run_tray
        _disk_check_callback()  # Initial tooltip
        run_tray(port=port)
    else:
        run_server(port=port)

# Debug Startup / Tray (Windows Cleaner)

## Purpose
Troubleshoot "app won't start" or "no tray icon" by following a fixed order and using logs and the console exe.

## 1. Run API only first
```bash
python run.py --no-tray
```
- If this fails, the problem is in backend/API or config. Check the log file (below).
- If it works, open http://127.0.0.1:8765/api/health to confirm.

## 2. Run with GUI (tray)
```bash
python run.py --gui
```
- If the tray never appears or the window doesn't open, the failure is likely in pystray/PIL or PyWebView. Check the same log file.

## 3. Log file
- Path: `%APPDATA%\WindowsCleaner\logs\windows_cleaner.log`
- The first line is a bootstrap entry (e.g. "bootstrap started"). Later lines include "main thread failed", "server thread failed", or "tray: ImportError" when something goes wrong.
- Open the log and read from the top to see the last successful step and the first error.

## 4. Packed exe with console
If the issue only happens with the built exe:
```bash
python packaging/build_exe.py --console
```
Run `dist/WindowsCleaner_console/WindowsCleaner_console.exe`. A console window will show prints and uncaught exceptions. Combine this with the log file for full context.

## 5. Common errors
- **ImportError / pystray / PIL**: Tray dependencies missing → log will mention "tray: ImportError".
- **Address already in use**: Port 8765 in use → try `python run.py --no-tray --port 8766`.
- **main thread failed / server thread failed**: See the traceback in the log for the exact line and module.

Full guide: [docs/DEBUGGING.md](../../docs/DEBUGGING.md).

# Run API Only (Windows Cleaner)

## Purpose
Start the Windows Cleaner backend in API-only mode: no tray icon, no main window. Use this for quick API testing or when working on backend/API only.

## Command
From the project root:

```bash
python run.py --no-tray
```

Or:

```bash
python -m backend.main
```

## After start
- Service listens at **http://127.0.0.1:8765** (or `--port` if set).
- Useful endpoints: `/api/health`, `/api/config`, `/api/disk/drives`.
- Logs: `%APPDATA%\WindowsCleaner\logs\windows_cleaner.log`.

Verify with: open http://127.0.0.1:8765/api/health in a browser or run `curl -s http://127.0.0.1:8765/api/health`.

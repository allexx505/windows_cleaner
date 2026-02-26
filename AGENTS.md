# AGENTS.md

## Cursor Cloud specific instructions

### Overview

Windows Cleaner is a Windows-targeted disk monitoring and file cleanup tool with a Python/FastAPI backend and Vue 3/Vite frontend. On Linux, the backend API and frontend work fully; Windows-specific features (system tray, USN journal, registry auto-start, toast notifications) gracefully degrade.

### Linux compatibility: winreg stub

`backend/utils/startup.py` does `import winreg` at the top level (a Windows-only stdlib module). A stub `winreg.py` is installed in `~/.local/lib/python3.12/site-packages/` to provide no-op implementations. This stub is also used by Python's `mimetypes` module (which conditionally reads the Windows registry). If the stub is missing, the backend will crash on import. The update script reinstalls it automatically.

### Running services

- **Backend API**: `python3 run.py --no-tray --port 8765` from workspace root. Serves the Vue SPA from `frontend/dist/` if built.
- **Frontend dev server**: `cd frontend && npm run dev` (Vite on port 5173, proxies `/api` to `localhost:8765`).
- **Frontend production build**: `cd frontend && npm run build` (outputs to `frontend/dist/`).
- Build the frontend before starting the backend if you want the SPA served at `/`.

### Testing

- **Backend tests**: `pytest backend/tests/ -v` (17 tests covering config, disk, index, resource guard, and API).
- See `README.md` and `docs/DEBUGGING.md` for additional run/debug instructions.

### API

FastAPI auto-docs at `http://127.0.0.1:8765/docs`. Key endpoints: `/api/health`, `/api/config` (GET/POST), `/api/disk/drives`, `/api/scan/large-files`.

### Gotchas

- Disk drives API returns `[]` on Linux (no Windows drive letters detected).
- The `frontend/node_modules` shipped in the repo was built for Windows. Run `rm -rf frontend/node_modules && npm install` in `frontend/` to get Linux-compatible binaries (the update script handles this).

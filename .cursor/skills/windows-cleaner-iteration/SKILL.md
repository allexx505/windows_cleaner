---
name: windows-cleaner-iteration
description: Iterate or fix bugs on the Windows Cleaner project. Use when modifying this repo: disk monitoring, cleanup rules, tray, PyWebView, bootstrap logging, or packaging. Familiar with run.py, backend/main.py, tray_service, constants, packaging/build_exe.py; always run pytest backend/tests/ after code changes and ensure frontend is built before packaging.
---

# Windows Cleaner Iteration

## Context
- Development history and quick reference: [docs/DEVELOPMENT_HISTORY.md](../../docs/DEVELOPMENT_HISTORY.md).
- Entry points: `run.py` (launcher / PyInstaller), `backend/main.py` (FastAPI + tray + optional PyWebView).
- Key files: `backend/main.py`, `backend/services/tray_service.py`, `backend/core/constants.py`, `backend/core/logging_config.py`, `packaging/build_exe.py`, `run.py`.

## Before changing behavior
- Run tests: `pytest backend/tests/ -v`. Fix any failures first.
- For packaging or release: ensure `frontend` is built (`cd frontend && npm run build && cd ..`) and `backend/core/constants.py` has the correct `APP_VERSION`.

## Conventions
- Config dir: `%APPDATA%\WindowsCleaner`; logs under `logs/windows_cleaner.log`; bootstrap log written earliest in `run.py`.
- Single process; resource guard and batched/low-priority scanning. See project rule `windows-cleaner-conventions.mdc` and [docs/DEBUGGING.md](../../docs/DEBUGGING.md) for troubleshooting.

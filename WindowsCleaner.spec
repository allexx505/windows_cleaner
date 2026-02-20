# PyInstaller spec for Windows Cleaner. Run: pyinstaller WindowsCleaner.spec
# From project root; requires frontend/dist to exist (npm run build in frontend/).

import os
import sys

ROOT = os.path.abspath(SPECPATH)
DIST_FRONTEND = os.path.join(ROOT, 'frontend', 'dist')

# Data: bundle frontend SPA so the exe can serve the web UI
datas = []
if os.path.isdir(DIST_FRONTEND):
    datas.append((DIST_FRONTEND, 'frontend/dist'))

# Ensure backend and deps are found
pathex = [ROOT]

# Hidden imports so PyInstaller collects the whole app
hiddenimports = [
    'backend',
    'backend.main',
    'backend.api',
    'backend.api.routes',
    'backend.core',
    'backend.core.config',
    'backend.core.constants',
    'backend.core.logging_config',
    'backend.services',
    'backend.services.monitor_service',
    'backend.services.notification_service',
    'backend.services.tray_service',
    'backend.services.resource_guard',
    'backend.services.index_service',
    'backend.utils',
    'backend.utils.disk',
    'backend.utils.usn_journal',
    'backend.utils.startup',
    'uvicorn.logging',
    'uvicorn.loops',
    'uvicorn.loops.auto',
    'uvicorn.protocols',
    'uvicorn.protocols.http',
    'uvicorn.protocols.http.auto',
    'uvicorn.protocols.websockets',
    'uvicorn.protocols.websockets.auto',
    'uvicorn.lifespan',
    'uvicorn.lifespan.on',
    'pystray',
    'PIL',
    'PIL._tkinter_finder',
    'desktop_notifier',
    'psutil',
]

a = Analysis(
    [os.path.join(ROOT, 'run.py')],
    pathex=pathex,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='WindowsCleaner',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,  # no console for GUI app
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name='WindowsCleaner',
)

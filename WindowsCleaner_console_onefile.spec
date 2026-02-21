# PyInstaller spec for Windows Cleaner (single-file exe with console for debugging).
# Run: pyinstaller WindowsCleaner_console_onefile.spec
# Or: python packaging/build_exe.py --onefile --console
# Output: dist/WindowsCleaner_console.exe (single file with console)

import os
import sys
from PyInstaller.utils.hooks import collect_all, collect_submodules

ROOT = os.path.abspath(SPECPATH)
DIST_FRONTEND = os.path.join(ROOT, 'frontend', 'dist')

datas = []
binaries = []
hiddenimports_extra = []

if os.path.isdir(DIST_FRONTEND):
    datas.append((DIST_FRONTEND, 'frontend/dist'))

# Include app icon for tray
ICON_PATH = os.path.join(ROOT, 'assets', 'app_icon.ico')
if os.path.isfile(ICON_PATH):
    datas.append((ICON_PATH, 'assets'))

# Collect pystray completely (it uses dynamic imports)
try:
    pystray_datas, pystray_binaries, pystray_hiddenimports = collect_all('pystray')
    datas += pystray_datas
    binaries += pystray_binaries
    hiddenimports_extra += pystray_hiddenimports
except Exception:
    pass
# Manually add pystray submodules
hiddenimports_extra += collect_submodules('pystray')

# Collect PIL/Pillow completely
pillow_datas, pillow_binaries, pillow_hiddenimports = collect_all('PIL')
datas += pillow_datas
binaries += pillow_binaries
hiddenimports_extra += pillow_hiddenimports

# Collect webview completely
try:
    webview_datas, webview_binaries, webview_hiddenimports = collect_all('webview')
    datas += webview_datas
    binaries += webview_binaries
    hiddenimports_extra += webview_hiddenimports
except Exception:
    pass
hiddenimports_extra += collect_submodules('webview')

pathex = [ROOT]

hiddenimports = hiddenimports_extra + [
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
    'webview',
    'webview.platforms',
    'webview.platforms.edgechromium',
    'webview.platforms.mshtml',
    'webview.platforms.winforms',
    'clr_loader',
    'pythonnet',
    'tkinter',
    'tkinter.filedialog',
]

a = Analysis(
    [os.path.join(ROOT, 'run.py')],
    pathex=pathex,
    binaries=binaries,
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
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='WindowsCleaner_console',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=True,  # show console for debugging
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=os.path.join(ROOT, 'assets', 'app_icon.ico'),
)

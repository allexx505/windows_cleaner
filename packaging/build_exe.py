"""
Build Windows Cleaner into a directory (and optional zip for GitHub Release).
Run from project root: python packaging/build_exe.py [--zip]

Prerequisites:
  - pip install -r requirements.txt pyinstaller
  - cd frontend && npm install && npm run build && cd ..
"""
import os
import subprocess
import sys
import zipfile

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DIST_FRONTEND = os.path.join(ROOT, "frontend", "dist")
SPEC = os.path.join(ROOT, "WindowsCleaner.spec")
SPEC_CONSOLE = os.path.join(ROOT, "WindowsCleaner_console.spec")
SPEC_ONEFILE = os.path.join(ROOT, "WindowsCleaner_onefile.spec")
SPEC_CONSOLE_ONEFILE = os.path.join(ROOT, "WindowsCleaner_console_onefile.spec")
OUTPUT_DIR = os.path.join(ROOT, "dist")
EXE_DIR = os.path.join(OUTPUT_DIR, "WindowsCleaner")
EXE_DIR_CONSOLE = os.path.join(OUTPUT_DIR, "WindowsCleaner_console")


def main() -> None:
    os.chdir(ROOT)
    console_build = "--console" in sys.argv or "--debug" in sys.argv
    onefile_build = "--onefile" in sys.argv or "--zip" in sys.argv
    if onefile_build and console_build:
        spec = SPEC_CONSOLE_ONEFILE
        exe_dir = OUTPUT_DIR
    elif onefile_build:
        spec = SPEC_ONEFILE
        exe_dir = OUTPUT_DIR
    elif console_build:
        spec = SPEC_CONSOLE
        exe_dir = EXE_DIR_CONSOLE
    else:
        spec = SPEC
        exe_dir = EXE_DIR
    if not os.path.isfile(spec):
        print(spec, "not found")
        sys.exit(1)
    if not os.path.isdir(DIST_FRONTEND) or not os.path.isfile(os.path.join(DIST_FRONTEND, "index.html")):
        print("Frontend not built. Run: cd frontend && npm install && npm run build")
        sys.exit(1)
    if ROOT not in sys.path:
        sys.path.insert(0, ROOT)

    # Build with PyInstaller using the spec
    r = subprocess.run([sys.executable, "-m", "PyInstaller", "--noconfirm", "--clean", spec])
    if r.returncode != 0:
        sys.exit(r.returncode)

    print("Build done. Output:", exe_dir)

    # Optional: create zip for GitHub Release
    if "--zip" in sys.argv and not console_build:
        version = "0.1.0"
        try:
            from backend.core.constants import APP_VERSION
            version = APP_VERSION
        except Exception:
            pass
        zip_name = os.path.join(OUTPUT_DIR, f"WindowsCleaner-v{version}-win64.zip")
        exe_path = os.path.join(OUTPUT_DIR, "WindowsCleaner.exe")
        with zipfile.ZipFile(zip_name, "w", zipfile.ZIP_DEFLATED) as zf:
            if os.path.isfile(exe_path):
                zf.write(exe_path, "WindowsCleaner.exe")
            elif os.path.isdir(EXE_DIR):
                for root, _dirs, files in os.walk(EXE_DIR):
                    for f in files:
                        path = os.path.join(root, f)
                        arc = os.path.join("WindowsCleaner", os.path.relpath(path, EXE_DIR))
                        zf.write(path, arc)
        print("Zip created:", zip_name)


if __name__ == "__main__":
    main()

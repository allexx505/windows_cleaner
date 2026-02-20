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
OUTPUT_DIR = os.path.join(ROOT, "dist")
EXE_DIR = os.path.join(OUTPUT_DIR, "WindowsCleaner")


def main() -> None:
    os.chdir(ROOT)
    if not os.path.isfile(SPEC):
        print("WindowsCleaner.spec not found")
        sys.exit(1)
    if not os.path.isdir(DIST_FRONTEND) or not os.path.isfile(os.path.join(DIST_FRONTEND, "index.html")):
        print("Frontend not built. Run: cd frontend && npm install && npm run build")
        sys.exit(1)
    if ROOT not in sys.path:
        sys.path.insert(0, ROOT)

    # Build with PyInstaller using the spec
    r = subprocess.run([sys.executable, "-m", "PyInstaller", "--noconfirm", "--clean", SPEC])
    if r.returncode != 0:
        sys.exit(r.returncode)

    print("Build done. Output:", EXE_DIR)

    # Optional: create zip for GitHub Release (name follows common convention)
    if "--zip" in sys.argv:
        version = "0.1.0"
        try:
            from backend.core.constants import APP_VERSION
            version = APP_VERSION
        except Exception:
            pass
        zip_name = os.path.join(OUTPUT_DIR, f"WindowsCleaner-v{version}-win64.zip")
        with zipfile.ZipFile(zip_name, "w", zipfile.ZIP_DEFLATED) as zf:
            for root, _dirs, files in os.walk(EXE_DIR):
                for f in files:
                    path = os.path.join(root, f)
                    arc = os.path.join("WindowsCleaner", os.path.relpath(path, EXE_DIR))
                    zf.write(path, arc)
        print("Zip created:", zip_name)


if __name__ == "__main__":
    main()

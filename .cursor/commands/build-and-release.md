# Build and Release (Windows Cleaner)

## Purpose
Build the frontend, run PyInstaller to produce the exe (and optionally the release zip), and prepare for GitHub Release.

## Steps

1. **Update version** (if releasing)
   - Set `APP_VERSION` in `backend/core/constants.py` to the release version (e.g. `0.1.0`). It should match the Git tag you will push (e.g. `v0.1.0`).

2. **Build frontend**
   ```bash
   cd frontend
   npm install
   npm run build
   cd ..
   ```

3. **Package**
   - Standard build: `python packaging/build_exe.py`
   - Release zip: `python packaging/build_exe.py --zip` → produces `dist/WindowsCleaner-vX.Y.Z-win64.zip`
   - Debug exe (with console): `python packaging/build_exe.py --console`

4. **Release (optional)**
   - Commit and push your changes.
   - Create and push a version tag: `git tag vX.Y.Z` then `git push origin vX.Y.Z`.
   - GitHub Actions will build and attach the zip to the new Release.

See [packaging/README_PACK.md](../../packaging/README_PACK.md) for details and troubleshooting.

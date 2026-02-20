# 打包说明 (Windows 文件清理工具)

## 环境要求

- Windows 10/11
- Python 3.10+（建议 3.11）
- Node.js 18+ 与 npm（用于构建前端）
- 已安装项目依赖（见根目录 `requirements.txt`）

## 步骤

### 1. 安装 Python 依赖

在项目根目录执行：

```bash
pip install -r requirements.txt
pip install pyinstaller
```

### 2. 构建前端 (Vue)

进入前端目录并构建生产包：

```bash
cd frontend
npm install
npm run build
cd ..
```

构建完成后，`frontend/dist` 下会生成静态文件（index.html 与 assets/）。

### 3. 使用 PyInstaller 打包

在项目根目录执行：

```bash
python packaging/build_exe.py
```

或手动执行等价命令（见 `build_exe.py` 内注释）。

打包完成后，可执行文件与依赖在 `dist/WindowsCleaner/` 目录下，主程序为 `WindowsCleaner.exe`。

### 4. 运行打包后的程序

- 直接运行：双击 `WindowsCleaner.exe`，将启动托盘图标；从托盘菜单选择「打开」可打开配置界面（内置网页或 PyWebView）。
- 带参数：`WindowsCleaner.exe --gui` 启动托盘；`WindowsCleaner.exe --no-tray` 仅启动 API 服务（无托盘）。

## 产物说明

- `dist/WindowsCleaner/WindowsCleaner.exe`：主程序
- 同目录下为依赖 DLL 与 Python 运行时；`frontend/dist` 会被打包进程序或同目录，供内置网页使用。

## 符合 GitHub 发布规范

- **版本号**：与 `backend/core/constants.py` 中 `APP_VERSION` 一致；发布时建议与 Git 标签一致（如 `v0.1.0`）。
- **打包产出**：`packaging/build_exe.py --zip` 会在 `dist/` 下生成 `WindowsCleaner-vX.Y.Z-win64.zip`，解压后为 `WindowsCleaner/` 目录，内含 `WindowsCleaner.exe` 及依赖，可直接作为 Release 附件分发。
- **自动发布**：仓库已配置 GitHub Actions（`.github/workflows/release.yml`）。推送版本标签即可自动构建并创建 Release：
  1. 在本地或 GitHub 创建标签，例如：`git tag v0.1.0`
  2. 推送标签：`git push origin v0.1.0`
  3. Actions 在 Windows 上构建前端与 exe，生成 zip 并创建 GitHub Release，附件名为 `WindowsCleaner-v0.1.0-win64.zip`（以当前代码中的 `APP_VERSION` 为准）。
- **发布检查**：发布前请确认已运行过 `frontend` 的 `npm run build` 且 `backend/core/constants.py` 中版本号已更新。

## 常见问题

- **杀毒软件误报**：PyInstaller 打包的 exe 可能被部分杀毒软件标记，可加入白名单或使用代码签名。
- **USN 不可用**：NTFS 卷的 USN 增量扫描可能需要管理员权限；无权限时自动退化为全量扫描。
- **端口占用**：默认使用 `127.0.0.1:8765`；若被占用可指定 `--port 其他端口`。

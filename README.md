# Windows 文件清理工具 (Windows Cleaner)

Windows 下的轻量级文件清理与磁盘监控工具：支持类似 Everything 的快速扫描思路（NTFS USN Journal）、大文件与垃圾目录监控、清理规则与阈值提醒，并提供 GUI、内置网页与外置 API。

**本项目使用 [Cursor](https://cursor.com) 全程开发，欢迎提出建议与反馈，后续会继续使用 Cursor 进行优化。**

---

## 功能概览

- **磁盘空间监控与阈值提醒**：按盘符或全局设定剩余空间百分比阈值，低于阈值时通过 Windows 通知或邮件提醒。
- **按盘符/目录的清理规则**：针对指定路径配置规则（大文件、按扩展名、垃圾目录），支持定期扫描并提醒或自动清理。
- **垃圾文件监控与清理**：预置常见 Windows 临时/缓存目录，可配置仅提醒或自动清理。
- **规则配置与扫描更新**：通过界面或 API 管理规则，支持立即执行扫描与索引重建。
- **自启动**：可选开机自启动（写入当前用户 Run 键）。
- **关闭行为**：关闭主窗口时可选择「最小化到托盘」或「直接退出」。
- **托盘悬停展示**：托盘图标悬停显示各盘剩余空间与垃圾目录大小概览。
- **通知方式**：Windows 通知栏 + 可选邮件通知（需配置 SMTP 与接收邮箱）。
- **多种使用方式**：双击运行有 GUI（托盘 + 内置网页/PyWebView）；也可直接访问 `http://127.0.0.1:8765` 使用内置网页；外置 REST API 供其他软件调用（磁盘状态、规则、扫描等）。

---

## 技术栈

- **后端**：Python 3.10+，FastAPI，pystray，PyWebView，pywin32，APScheduler，desktop-notifier，psutil
- **前端**：Vue 3，Vue Router，Pinia，Axios，Vite

---

## 安装与运行

### 方式一：从源码运行

1. 克隆仓库，进入项目目录。
2. 安装依赖：`pip install -r requirements.txt`
3. （可选）构建前端：`cd frontend && npm install && npm run build && cd ..`
4. 启动：
   - 仅 API 服务：`python -m backend.main`
   - 托盘 + 内置网页：`python -m backend.main --gui`
5. 浏览器访问 `http://127.0.0.1:8765` 或从托盘菜单「打开」进入界面。

### 方式二：使用打包好的 exe（Release）

1. 在本仓库的 [Releases](https://github.com/allexx505/windows_cleaner/releases) 页面下载 `WindowsCleaner-vX.Y.Z-win64.zip`。
2. 解压后运行 `WindowsCleaner.exe`，托盘出现后从菜单「打开」进入设置与清理界面。

---

## 日志与问题排查

- 程序会将**本地日志**写入配置目录下的 `logs/windows_cleaner.log`。
- Windows 下配置目录一般为：`%APPDATA%\WindowsCleaner`，即 `C:\Users\<用户名>\AppData\Roaming\WindowsCleaner`。
- 日志为轮转文件（单文件约 2MB，最多保留 5 个备份），便于长期运行与问题排查。启动后首条日志会打印当前日志文件完整路径。

---

## 打包说明

详见 [packaging/README_PACK.md](packaging/README_PACK.md)，包括：

- 环境要求（Python、Node、PyInstaller）
- 前端构建与 `python packaging/build_exe.py [--zip]` 打包步骤
- **符合 GitHub 发布规范**：zip 命名、自动 Release 流程（推送 `v*` 标签触发构建并发布）

---

## 开发与贡献

- 本项目使用 **Cursor** 进行开发与迭代，欢迎通过 Issue 或 PR 提出建议与改进。
- 关键逻辑配有单元测试（`backend/tests/`），运行：`pytest backend/tests/`。

---

## 许可证

见 [LICENSE](LICENSE) 文件。

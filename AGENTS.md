# Windows Cleaner – Agent 说明

Windows 下轻量级磁盘监控与文件清理工具：FastAPI 后端 + Vue 3 前端，托盘 + 内置网页 + REST API。支持 NTFS USN 快速扫描、清理规则与阈值提醒。

## 开发环境
- Windows 10/11，Python 3.10+，Node.js 18+
- 依赖：`pip install -r requirements.txt`；前端：`cd frontend && npm install && npm run build && cd ..`

## 常用命令
- 仅 API：`python run.py --no-tray`
- 托盘 + 窗口：`python run.py --gui`
- 测试：`pytest backend/tests/ -v`
- 打包：`python packaging/build_exe.py`；Release zip：`--zip`；调试 exe：`--console`

## 配置与日志
- 配置目录：`%APPDATA%\WindowsCleaner`
- 日志文件：`%APPDATA%\WindowsCleaner\logs\windows_cleaner.log`

## 详细说明
- 开发与迭代：[docs/DEVELOPMENT_HISTORY.md](docs/DEVELOPMENT_HISTORY.md)
- 调试步骤：[docs/DEBUGGING.md](docs/DEBUGGING.md)
- 打包与发布：[packaging/README_PACK.md](packaging/README_PACK.md)

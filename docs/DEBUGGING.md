# 调试说明（Windows 文件清理工具）

本文档面向开发者与二次开发 AI，用于快速复现问题、验证改动和调试启动/配置流程。

## 从源码运行的几种方式

- **仅 API（无托盘、无窗口）**  
  ```bash
  python run.py --no-tray
  ```  
  服务监听 `http://127.0.0.1:8765`，可直接用浏览器或 curl 访问：
  - `/api/health` — 健康检查
  - `/api/config` — 当前配置
  - `/api/disk/drives` — 磁盘列表

- **带托盘与自动开窗**  
  ```bash
  python run.py --gui
  ```  
  需要 pystray、PIL；可选 pywebview 用于内置窗口。约 2 秒后自动打开主界面。

- **打包后**  
  - 普通 exe：无控制台，适合最终用户。  
  - 调试用：运行 `python packaging/build_exe.py --console` 生成 `WindowsCleaner_console.exe`，带控制台，便于查看 print 与未捕获异常。

## 日志位置与查看

- **路径**：`%APPDATA%\WindowsCleaner\logs\windows_cleaner.log`  
  - 与配置目录一致：`%APPDATA%\WindowsCleaner\` 下还有 `config.json` 等。
- **内容**：启动时最早会写入 bootstrap 记录（时间戳 + `bootstrap started` 等），随后为正常业务日志与 uvicorn 请求日志。
- **常见错误对应**：
  - `ImportError`、`pystray`、`PIL`：托盘依赖缺失，会写入 `tray: ImportError`。
  - `server thread failed`：后台 API 服务启动或运行异常，见下方完整栈。
  - `main thread failed`：主流程某步异常（如 setup_logging、run_tray 前逻辑）。
  - 端口占用：日志中可能出现 bind 或 address already in use；可先 `run.py --no-tray --port 8766` 换端口验证。

## 单元测试

在项目根目录执行：

```bash
pytest backend/tests/ -v
```

- **覆盖模块**：  
  - `test_config.py` — 配置加载/校验、磁盘阈值与清理规则结构。  
  - `test_disk.py` — 磁盘信息接口。  
  - `test_index_service.py` — 索引与扫描。  
  - `test_resource_guard.py` — 资源限制逻辑。  
- **只跑单个文件**：`pytest backend/tests/test_config.py -v`  
- **只跑单个用例**：`pytest backend/tests/test_config.py::test_load_config -v`

## 推荐调试顺序

1. 先 `python run.py --no-tray`，确认 API 与日志正常（访问 `/api/health`、查看日志文件是否有 bootstrap 与启动记录）。  
2. 再试 `python run.py --gui`，看托盘与自动开窗是否正常。  
3. 若打包后出现「无法打开、无托盘」，用 `WindowsCleaner_console.exe` 复现，查看控制台输出与上述日志文件。

## 模拟打开并配置规则（手动步骤）

用于验证「打开应用 → 配置磁盘清理规则 → 确认生效」的完整流程。

1. **启动服务**  
   - API 仅：`python run.py --no-tray`  
   - 或完整 GUI：`python run.py --gui`

2. **打开界面**  
   - 浏览器访问：http://127.0.0.1:8765  
   - 或从托盘菜单选择「打开」

3. **添加配置**  
   - 在「设置」或「规则」页添加一条**磁盘阈值**（如 C: 剩余低于 15% 提醒）和一条**清理规则**（如某路径下大于 100MB 的大文件、仅提醒）。  
   - 保存。

4. **确认已保存**  
   - 刷新页面或再次打开配置/规则页，确认阈值与规则存在。  
   - 或直接调用接口验证：  
     ```bash
     curl -s http://127.0.0.1:8765/api/config
     ```  
     检查返回的 `disk_thresholds`、`cleanup_rules` 与刚配置一致。

5. **规则生效说明**  
   - 定时任务会在内部间隔（见 `backend/core/constants.py`）执行 `run_scheduled_rules` 与 `check_disk_thresholds`。  
   - 也可通过脚本 `scripts/simulate_open_and_configure.py` 在服务已启动的前提下，用 API 写入配置并断言返回，做「配置并验证」的自动化回归。

## 仅启动后端（脚本）

需要只起 API、不启托盘时，可从项目根目录执行：

- **PowerShell**：`.\scripts\run_api_only.ps1`  
- 脚本会启动 `python run.py --no-tray` 并输出日志路径与 `http://127.0.0.1:8765`，便于后续用浏览器或 curl 验证接口。

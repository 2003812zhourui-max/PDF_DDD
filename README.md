# PDF_D

WMS PDF 面单下载、面单类型识别、条码校验和 Excel/JSON 导出工具。

主入口是 `main.py`。默认流程是：

1. 从 WMS 按时间、仓库、状态、渠道下载 PDF 面单。
2. 识别 PDF 中的承运商、跟踪号、面单类型和 0024 子类型。
3. 结合下载日志和 metadata 补充渠道、客户、仓库等信息。
4. 导出 Excel 和 JSON，方便人工复核和后续统计。

## 新电脑初始化

在新 Windows 电脑上先安装 Git 和 Python 3.11 或更高版本，然后执行：

```powershell
git clone <你的仓库地址>
cd PDF_D
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m playwright install chromium
```

如果需要 OCR，还要额外安装 Tesseract OCR，并确保 `tesseract.exe` 在系统 `PATH` 中。

## 本地配置

每台电脑都保留自己的 `config.json`，不要提交到 Git。

```powershell
Copy-Item config.example.json config.json
notepad config.json
```

`config.json` 支持配置 WMS 地址、账号密码、默认下载时间范围、仓库、状态、输出目录、登录态路径等。账号密码也可以不写入 `config.json`，改用当前 PowerShell 会话环境变量：

```powershell
$env:WMS_USERNAME="你的WMS账号"
$env:WMS_PASSWORD="你的WMS密码"
```

命令行参数优先级最高，可以覆盖 `config.json`。

## 运行项目

查看参数，不连接业务系统：

```powershell
python main.py --help
```

下载并识别一批面单：

```powershell
python main.py --start-time "2026-06-10 00:00:00" --end-time "2026-06-10 23:59:59" --wh-codes US02 --statuses 15 --workers 5 --limit 200 --output-name download_200_check
```

只识别本地已有 PDF：

```powershell
python main.py --input-dir pdf_downloads --download-log logs\download_log.csv --output-dir output\pdf --output-name local_check
```

使用浏览器模式：

```powershell
python main.py --browser-mode --start-time "2026-06-10 00:00:00" --end-time "2026-06-10 23:59:59" --wh-codes US02
```

Windows 双击启动可以使用 `run.bat`。它会自动进入项目目录、激活 `.venv` 并执行 `main.py`。如果需要传参，建议在 PowerShell 里运行：

```powershell
.\run.bat --help
```

## 常见问题

登录态失效：删除或重新生成 `wms_storage_state.json`，或重新设置 `WMS_USERNAME`、`WMS_PASSWORD` 后再运行。

IP 白名单或风控限制：如果新电脑或新网络无法登录 WMS，先确认业务系统是否限制登录 IP、设备或二次验证。

Playwright 报浏览器不存在：执行 `python -m playwright install chromium`。

依赖安装失败：先升级 pip；如 `zxing-cpp` 或 `PyMuPDF` 安装失败，确认 Python 版本和系统架构是 Windows x64，并尝试重新安装对应依赖。

路径问题：不要在代码里写 `C:\Users\...` 这种本机绝对路径。需要改目录时优先改 `config.json`，相对路径会基于项目根目录解析。

账号密码泄露风险：不要提交 `.env`、`config.json`、`wms_storage_state.json`、任何 cookie/token/密码文件。

## 不提交到 Git 的文件

以下文件和目录只保留在本机：

- `.venv/`、`venv/`
- `config.json`、`.env`
- `wms_storage_state.json`、`storage_state.json`、`.wms_token_cache.json`
- `logs/`、`output/`、`downloads/`、`pdf_downloads/`
- `build/`、`dist/`、`*.spec`
- 浏览器缓存、临时 Excel、CSV、JSONL、ZIP 等运行产物

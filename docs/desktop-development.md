# 桌面版开发与构建

## 最小架构

`micas_ppt.desktop` 提供 Tkinter 界面和本地任务适配器，直接调用 `engine.convert(..., allow_risk=False)`，不复制转换逻辑。一个后台线程执行转换，通过 Queue 发送状态和终态；Tk 主线程每 100ms 轮询，所有控件更新仅在主线程执行。任务运行时禁止重复启动和退出，避免中途写文件。没有服务器、FastAPI、飞书集成或网络客户端。

每次任务先在输出目录的临时子目录生成结果，再用排他创建发布报告和 PPTX，已有文件不覆盖；失败时尽量保留报告。不保证系统断电时的事务原子性；异常中断可能留下临时目录。错误会显示并可重试。GUI 不提供 `--allow-risk`，CLI 参数保持原样。

资源通过 `sys._MEIPASS`（打包后）或仓库根目录（开发时）定位。PyInstaller spec 只显式包含官方 PPTX、映射和 catalog，另收集 tkinterdnd2 的跨平台拖拽依赖；不会扫描工作目录或收录客户文件。原始模板继续使用 catalog SHA-256 校验。未改模板或登记清单。

## 开发和验证

需要带 Tcl/Tk 的 Python 3.12；平台包构建推荐使用与 CI 相同的版本。Tkinter 不通过 pip 安装。开发依赖：

```bash
python -m pip install -e '.[desktop,build]'
python -m micas_ppt.desktop
python -m unittest discover -s tests -v
python -m micas_ppt.desktop --smoke-test
python scripts/validate_templates.py
```

GUI 测试在无显示的主机上会明确 skip；有显示时验证控件状态、带空格中文拖入路径、后台线程处理时事件循环响应和防止重复启动。任务测试覆盖不覆盖原稿/已有输出、重复转换命名、失败报告、安全模式和 frozen 资源路径。smoke test 创建真实窗口并转换合成 PPTX，核验内置模板和文字输出。测试不使用真实客户文件。

引擎只做 UTF-8 读写兼容修复，避免 Windows 系统默认编码导致中文 catalog/报告读取失败；转换布局算法不变。CLI 继续支持 `micas-ppt` 和 `python -m micas_ppt.cli`。

## 各系统原生构建

PyInstaller 不是交叉编译器，必须在目标系统构建：

```powershell
# Windows PowerShell，在仓库目录
./scripts/build-windows.ps1
```

```bash
# macOS
./scripts/build-macos.sh
```

Windows 产物为包含独立 exe 和资源目录的便携 ZIP；macOS 产物为包含 .app 的 ZIP。二者无需目标用户安装 Python；不是单文件 exe，也不是 MSI/DMG 安装器。输出在 `dist/`，构建中间文件在 `build/`，均被 gitignore 排除。

工作流 `.github/workflows/build-desktop.yml` 在开发分支相关变更 push 或手动触发时，分别使用 `windows-latest`、`macos-latest` Runner，执行测试、源码 GUI 冒烟、原生构建和打包后应用冒烟，然后上传 ZIP 为 30 天有效的 Actions artifacts。只上传明确命名的构建 ZIP。产物名标明 OS 和 Runner 架构；macOS 不是 Universal，暂不额外构建另一种架构。

用户获得的产物应来自所有检查成功的运行，管理员下载后按公司渠道分发。工作流不创建 Release，不发布到 main，也不会包含本地真实测试产物。尚未实现代码签名、公证、自动更新或安装器；签名凭据需要公司维护者另行配置。

# 项目过程记录

## 项目标题
Tushare 股票数据可视化分析实验

## 对话与实施日志

### 2026-04-01 轮次 1
- 接收需求：需要完整实现 4 道 Tushare 数据可视化相关作业。
- 额外要求确认：
  - 需要我为项目设定标题。
  - 需要初始化 Git 仓库。
  - 需要推送到用户的 GitHub 仓库。
  - 需要建立专门文档目录保存过程文档。
  - 需要在每次对话更新时同步更新该文档。
- 当前工作区 `F:\YL-Workspace\Z-2` 为空目录。
- 当前目录尚未初始化为 Git 仓库。
- 尝试访问作业原始链接 `https://www.yuque.com/beiweiqiaomu/pugark/kkrpslzxo5gcbtxy?singleDoc`，外部抓取返回 `403 Forbidden`。
- 决策：以用户消息中已给出的完整题目细则作为本次实现依据，并在后续交付文档中明确说明。
- 环境检查结果：
  - `Python 3.14.3`
  - `pip 25.3`
  - `git 2.46.2.windows.1`
  - `gh` 未安装，不可直接使用 GitHub CLI 工作流。
- 通过 GitHub 连接器识别到用户账号为 `XXYoLoong`（显示名 `Jiacheng Ni`），并可列出其可访问仓库。
- 当前阻塞点：需要确认如何在本机认证条件下完成远程 GitHub 仓库创建与推送。
- 检查结果：
  - Git 全局配置存在 `credential.helper=manager` 与 `credential.helper=store`。
  - 发现环境变量名称 `GITHUB_ACCESS_TOKEN_YOLOONG`，说明本机可能具备 GitHub API/推送认证条件。
- 制定实施计划：
  1. 搭建项目目录、配置文件和过程文档机制。
  2. 实现 Tushare 数据获取、清洗、分析与可视化代码。
  3. 生成 Word 实验报告与辅助文档。
  4. 安装依赖并运行脚本验证输出。
  5. 初始化 Git、创建 GitHub 仓库并推送代码。
- 下一步：开始搭建项目骨架与基础配置文件。

### 2026-04-01 轮次 2
- 已创建基础项目文件：
  - `.gitignore`
  - `.env.example`
  - `README.md`
  - `requirements.txt`
  - `src/__init__.py`
  - `src/config.py`
  - `src/main.py`
- 已确定目录约定：
  - `docs/` 保存过程文档与说明
  - `outputs/charts/` 保存图表
  - `outputs/data/` 保存结果数据
  - `outputs/report/` 保存 Word 报告
- 已在配置中约定默认研究股票：
  - 题目一：贵州茅台 `600519.SH`
  - 题目二：中国平安 `601318.SH`、比亚迪 `002594.SZ`、贵州茅台 `600519.SH`
  - 题目三：比亚迪 `002594.SZ`
- 已采用 `.env` 读取 `TUSHARE_TOKEN`，避免将用户 token 提交到 GitHub。
- 下一步：实现数据下载、清洗、统计分析、可视化和交易信号逻辑。

### 2026-04-01 轮次 3
- 已完成核心实现文件：
  - `src/analysis.py`：负责 Tushare 数据获取、清洗、指标计算、图表绘制、交易信号生成与结果汇总。
  - `src/report_builder.py`：负责生成包含实验结果和代码附录的 Word 报告。
  - `src/main.py`：串联分析流程与报告导出。
- 已覆盖题目要求：
  - 题目一：单只股票数据清洗、缺失/重复检查、成交量柱状图、月均收盘价折线图。
  - 题目二：3 只股票累计收益率计算与柱状图对比、任选 1 只股票均线图。
  - 题目三：5 日/20 日均线、日收益率、累计收益率、买卖信号、策略收益、表现分析。
- 已新增本地 `.env` 文件并写入用户提供的 Tushare token，仅用于本地运行，按 `.gitignore` 规则不会提交到 GitHub。
- 运行环境补充决策：
  - 检测到本机存在 Python 3.14、3.13、3.12、3.11、3.10 多版本。
  - 为提升第三方库兼容性，决定优先使用 Python 3.12 创建虚拟环境执行本项目。
- 实际执行中，`py -3.12 -m venv .venv` 因 `ensurepip` 非零退出而失败。
- 调整决策：改用 Python 3.11 创建虚拟环境，继续推进，不在 Python 3.12 环境问题上停滞。
- 实际执行中，`py -3.11 -m venv .venv` 同样在 `ensurepip` 阶段失败。
- 第二次调整决策：放弃虚拟环境方案，直接使用已可正常工作的 `Python 3.11 + pip` 安装项目依赖并运行。
- 执行 `py -3.11 -m pip install -r requirements.txt` 时失败，报错 `OSError: [Errno 28] No space left on device`。
- 初步判断：`pip` 下载/缓存临时目录所在磁盘空间不足。
- 下一步：检查各磁盘可用空间，并将 `pip` 缓存或临时目录切换到空间充足的位置后重试安装。

### 2026-04-01 轮次 4
- 磁盘检查结果：
  - `C:` 剩余约 `1.24 GB`
  - `D:` 剩余约 `31.41 GB`
  - `E:` 剩余约 `38.85 GB`
  - `F:` 剩余约 `41.01 GB`
- 发现 `pip cache dir` 位于 `C:\Users\Ni\AppData\Local\pip\cache`，与空间不足判断一致。
- 已创建本地临时目录 `.tmp` 和缓存目录 `.pip-cache`，并通过设置 `TEMP/TMP` 到 `F:\YL-Workspace\Z-2\.tmp` 成功安装依赖。
- 已安装关键依赖：
  - `tushare`
  - `pandas`
  - `matplotlib`
  - `numpy`
  - `python-docx`
  - `openpyxl`
- 已执行 `py -3.11 -m src.main`，程序运行成功。
- 已生成核心交付物：
  - Word 报告：`outputs/report/Tushare股票数据可视化分析实验报告.docx`
  - 汇总结果：`outputs/data/analysis_master_summary.json`
- 已确认输出目录中包含：
  - 7 张图表
  - 8 份明细/汇总数据文件
  - 1 份 Word 报告
- 已核验关键结果摘要：
  - 题目一 `600519.SH` 共 `243` 条记录，缺失值 `0`、重复值 `0`
  - 题目二最终累计收益率：`中国平安 +34.88%`、`比亚迪 -63.95%`、`贵州茅台 -7.45%`
  - 题目三买入信号 `8` 次、卖出信号 `8` 次，股票累计收益率约 `-71.92%`，策略累计收益率约 `-71.22%`
- 已通过 `python-docx` 读取 Word 报告前 20 段内容，确认报告包含：
  - 封面标题与生成时间
  - 实验说明
  - 三道题结果章节
  - 图表标题
  - 后续代码附录章节

### 2026-04-01 轮次 5
- 用户已确认：GitHub 新仓库可见性使用 `public`。
- 用户新增要求：
  - 如有帮助，可安装 `gh`。
  - 安装位置不要放在 `C:` 盘。
  - 建议安装到 `F:` 盘并加入环境变量。
- 执行决策：
  - 将 `gh` 安装到 `F:` 盘工具目录。
  - 将其加入当前会话与用户级 `Path` 环境变量。
  - 使用 `gh` 或 GitHub API 完成公开仓库创建与推送。
- 发布前补充调整：
  - 修改 `.gitignore`，不再忽略 `outputs/` 下的实验结果与 Word 报告，以便仓库保留交付物。
  - 增加 `.tmp/`、`.pip-cache/` 忽略规则，避免提交安装缓存。
  - 在 `README.md` 中注明题目四为选做项，本项目默认完成前三道必做题。
- 检查到环境变量 `GITHUB_ACCESS_TOKEN_YOLOONG` 已存在，可用于 GitHub 认证。
- 首次调用 GitHub Releases API 时因匿名请求触发限流，后续将改用带认证请求继续安装 `gh`。
- 已通过带认证请求获取 GitHub CLI 最新发布信息：
  - 版本：`v2.89.0`
  - 安装包：`gh_2.89.0_windows_amd64.zip`
- 已下载到 `F:\Tools\gh-cli\downloads\gh_2.89.0_windows_amd64.zip`
- 已解压到 `F:\Tools\gh-cli\app`
- 已确认可执行文件位置：`F:\Tools\gh-cli\app\bin\gh.exe`
- 已将 `F:\Tools\gh-cli\app\bin` 加入当前会话与用户级 `Path`。
- 已通过 `GH_TOKEN` 完成 `gh` 认证，当前账号为 `XXYoLoong`。
- 已使用 REST 接口确认目标仓库 `XXYoLoong/tushare-stock-visualization-lab` 当前不存在，可安全创建。
- 已在本地执行：
  - `git init -b main`
  - `git add .`
  - `git commit -m "Initialize Tushare stock visualization assignment"`
- 首次提交已成功，当前本地分支为 `main`。
- 已执行 `gh auth setup-git` 配置 Git 与 GitHub CLI 的认证联动。
- 已成功创建公开仓库：`https://github.com/XXYoLoong/tushare-stock-visualization-lab`
- 首次自动推送阶段出现网络错误：
  - `RPC failed; HTTP 408`
  - `the remote end hung up unexpectedly`
- 当前判断：远程仓库已创建成功，仅需重试推送即可完成发布。
- 已检查远程地址：
  - `origin fetch/push -> https://github.com/XXYoLoong/tushare-stock-visualization-lab.git`
- 已通过 `git ls-remote origin` 确认远程仓库可连通，且初始状态为空仓库。
- 已成功执行 `git push -u origin main`，完成首次推送。
- 当前状态：本地分支 `main` 已跟踪远程分支 `origin/main`。
- 已提交本轮过程文档更新：`Update project process log`
- 首次补推该提交时失败，原因是新 shell 会话未继承 `GH_TOKEN` 与 `gh` 路径，导致 Git 进入交互式认证并报错：
  - `/dev/tty: No such device or address`
  - `could not read Username for 'https://github.com'`
- 当前判断：仓库和提交均正常，只需在同一命令中补齐 `GH_TOKEN` 与 `gh` 环境后重新推送。
- 已在同一命令中补齐 `GH_TOKEN` 与 `gh` 路径环境。
- 已追加提交：`Record GitHub publish follow-up`
- 已成功推送到远程仓库：`https://github.com/XXYoLoong/tushare-stock-visualization-lab`
- 当前最终状态：
  - 本地仓库已初始化完成
  - GitHub 公开仓库已创建完成
  - `main` 分支代码与文档已同步到远程
  - `gh` 已安装在 `F:\Tools\gh-cli\app\bin` 并加入用户级 `Path`
- 本轮任务的实现、报告生成、版本管理和远程发布均已完成。
- 后续在推送 `Finalize delivery log` 提交时，出现一次临时网络错误：
  - `OpenSSL SSL_connect: SSL_ERROR_SYSCALL`
- 当前判断：属于瞬时网络波动，重试 `git push` 即可完成最终同步。
- 已再次提交过程文档修正：`Note final push retry`
- 已重试 `git push` 并成功同步到远程。
- 截至当前，远程仓库 `main` 分支已包含全部最终文件和完整过程日志。

### 2026-04-01 轮次 6
- 用户提出新要求：将“每次操作同步到过程文档”的做法抽象为可复用的全局 SKILL，并希望后续任何项目都尽量执行。
- 采用技能创建流程 `skill-creator` 处理该需求。
- 已在全局技能目录 `F:\.codex\skills` 下创建新技能：`process-log-sync`
- 已生成并完善以下文件：
  - `F:\.codex\skills\process-log-sync\SKILL.md`
  - `F:\.codex\skills\process-log-sync\references\log-template.md`
  - `F:\.codex\skills\process-log-sync\agents\openai.yaml`
- 技能内容已覆盖：
  - 优先复用现有过程文档，否则创建 `docs/step-by-step-log.md`
  - 在项目开始、每次实质性进展更新后、最终交付前同步更新过程文档
  - 记录高信号事实、避免噪音和敏感信息泄露
  - 提供通用日志模板
- 处理过程中的修正：
  - 初版技能文件包含非 ASCII 字符，导致 `quick_validate.py` 在 Windows 默认 `GBK` 读取时失败
  - 已将技能文件调整为纯 ASCII 内容并重新校验通过
- 已显式设置 `allow_implicit_invocation: true`，尽量让该技能在未来项目中可被默认隐式触发。
- 下一步：向用户说明该技能的实际生效边界，并给出使用建议。

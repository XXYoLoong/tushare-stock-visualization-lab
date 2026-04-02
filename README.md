# Tushare 股票数据可视化分析实验

基于 [Tushare](https://tushare.pro/) 的股票日线行情分析、收益率对比、趋势识别与交易信号可视化实验项目。运行后自动生成图表、清洗数据与 Word 实验报告。

## 功能概览

| 模块 | 说明 |
|------|------|
| 题目一 | 单只股票指定年度日线行情清洗、统计与可视化 |
| 题目二 | 多只股票累计收益率对比与均线分析 |
| 题目三 | 最近约一年趋势识别、均线信号与简单交易规则分析 |
| 报告 | 汇总结果并生成 Word 实验报告 |

说明：题目四在原作业中为选做项，本项目默认完成前三道必做题并生成提交所需报告。

## 技术栈

- **Python** 3.11 及以上（推荐 3.11+）
- **数据与接口**：`tushare`、`pandas`、`numpy`
- **可视化**：`matplotlib`
- **报告**：`python-docx`、`openpyxl`
- **配置**：`python-dotenv`（从 `.env` 读取 Tushare Token）

## 目录结构

```text
.
├── docs/                    # 过程文档、步骤说明等
├── src/                     # 源代码
│   ├── main.py              # 程序入口
│   ├── config.py            # 配置与加载 .env
│   ├── analysis.py          # 数据分析与图表生成逻辑
│   └── report_builder.py    # Word 报告构建
├── outputs/
│   ├── charts/              # 导出的图表（PNG 等）
│   ├── data/                # 清洗与汇总后的数据（JSON 等）
│   └── report/              # 生成的 Word 实验报告
├── requirements.txt         # Python 依赖锁定范围
├── .env.example             # 环境变量示例（复制为 .env 后填写）
└── README.md
```

## 环境准备

### 1. 安装 Python

请安装 **Python 3.11 或更高版本**，并确认已加入系统 `PATH`：

```bash
python --version
```

应显示 `Python 3.11.x` 或更高。

### 2. 创建虚拟环境（推荐）

在项目根目录下使用虚拟环境，可避免污染全局 Python，并便于复现实验环境。

**Windows（PowerShell 或 CMD）**

```bash
cd 你的项目路径\Z-2
python -m venv .venv
```

激活虚拟环境：

```powershell
# PowerShell
.\.venv\Scripts\Activate.ps1
```

若 PowerShell 提示脚本执行策略限制，可先执行（当前用户）：

```powershell
Set-ExecutionPolicy -RemoteSigned -Scope CurrentUser
```

或使用 CMD：

```cmd
.\.venv\Scripts\activate.bat
```

**macOS / Linux**

```bash
cd /path/to/Z-2
python3 -m venv .venv
source .venv/bin/activate
```

激活成功后，命令行前缀通常会出现 `(.venv)`。**之后所有 `pip` / `python` 命令都在该虚拟环境中执行。**

退出虚拟环境（任意系统）：

```bash
deactivate
```

> 本项目已在 `.gitignore` 中忽略 `.venv/`，请勿将虚拟环境目录提交到 Git。

### 3. 安装依赖

在**已激活**虚拟环境的终端中执行：

```bash
pip install -U pip
pip install -r requirements.txt
```

### 4. 配置 Tushare Token

1. 复制 `.env.example` 为 `.env`（与 `requirements.txt` 同级）。
2. 在 [Tushare 官网](https://tushare.pro/) 注册并获取 Token，填入 `.env` 中的 `TUSHARE_TOKEN`。

示例（值请换成你自己的 Token）：

```env
TUSHARE_TOKEN=你的token字符串
```

`.env` 仅用于本机，**不要**提交到公开仓库。

## 运行

在项目根目录、虚拟环境已激活的前提下：

```bash
python -m src.main
```

若未配置 Token，程序会提示 `Missing TUSHARE_TOKEN`，请先完成上一节的 `.env` 配置。

### 运行结果

成功后会在 `outputs/` 下生成或更新例如：

- **charts/**：各题对应的图表文件  
- **data/**：清洗与汇总后的数据（如 JSON）  
- **report/**：Word 实验报告路径会在终端最后一行打印  

终端示例输出中会包含 Word 报告路径与汇总结果文件路径。

## 默认标的说明

- **题目一**：贵州茅台 `600519.SH`  
- **题目二**：中国平安 `601318.SH`、比亚迪 `002594.SZ`、贵州茅台 `600519.SH`  
- **题目三**：比亚迪 `002594.SZ`  

具体年份与参数以 `src/config.py` 及分析逻辑为准。

## 常见问题

- **无法安装依赖**：确认使用的是项目虚拟环境里的 `python` / `pip`（`where python` 或 `which python` 应指向 `.venv`）。  
- **接口权限或数据为空**：Tushare 不同积分等级可调用接口不同，请对照官网说明检查 Token 与权限。  
- **图表中文乱码**：若系统缺少中文字体，可在本机安装常用黑体/宋体，或在代码中指定 `matplotlib` 字体（见 `src` 内相关设置）。

---

本项目用于课程或实验提交；数据来源于 Tushare，不构成任何投资建议。

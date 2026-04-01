from __future__ import annotations

import os
from dataclasses import dataclass, field
from datetime import date, timedelta
from pathlib import Path

from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parent.parent
DOCS_DIR = BASE_DIR / "docs"
OUTPUTS_DIR = BASE_DIR / "outputs"
CHARTS_DIR = OUTPUTS_DIR / "charts"
DATA_DIR = OUTPUTS_DIR / "data"
REPORT_DIR = OUTPUTS_DIR / "report"


@dataclass(frozen=True)
class StockInfo:
    ts_code: str
    name: str
    industry: str


@dataclass(frozen=True)
class Settings:
    project_title: str = "Tushare 股票数据可视化分析实验"
    token: str = ""
    task1_stock: StockInfo = StockInfo("600519.SH", "贵州茅台", "食品饮料")
    task2_stocks: tuple[StockInfo, ...] = (
        StockInfo("601318.SH", "中国平安", "金融保险"),
        StockInfo("002594.SZ", "比亚迪", "汽车新能源"),
        StockInfo("600519.SH", "贵州茅台", "食品饮料"),
    )
    task3_stock: StockInfo = StockInfo("002594.SZ", "比亚迪", "汽车新能源")
    task1_start: str = "20250101"
    task1_end: str = "20251231"
    task2_start: str = "20250101"
    task2_end: str = "20251231"
    task3_start: str = field(
        default_factory=lambda: (date.today() - timedelta(days=365)).strftime("%Y%m%d")
    )
    task3_end: str = field(default_factory=lambda: date.today().strftime("%Y%m%d"))


def ensure_directories() -> None:
    for path in (DOCS_DIR, OUTPUTS_DIR, CHARTS_DIR, DATA_DIR, REPORT_DIR):
        path.mkdir(parents=True, exist_ok=True)


def load_settings() -> Settings:
    load_dotenv()
    token = os.getenv("TUSHARE_TOKEN", "").strip()
    settings = Settings(token=token)
    ensure_directories()
    return settings

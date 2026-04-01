from __future__ import annotations

import json
import time
from dataclasses import dataclass
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import tushare as ts

from src.config import CHARTS_DIR, DATA_DIR, Settings, StockInfo


plt.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False


@dataclass(frozen=True)
class Task1Result:
    stock: StockInfo
    cleaned_data_file: Path
    monthly_mean_file: Path
    volume_chart: Path
    monthly_chart: Path
    summary_file: Path
    total_rows: int
    duplicate_rows: int
    missing_cells: int
    closing_price_mean: float
    closing_price_std: float
    volume_mean: float
    highest_close: float
    lowest_close: float


@dataclass(frozen=True)
class Task2Result:
    stocks: tuple[StockInfo, ...]
    combined_data_file: Path
    final_return_file: Path
    cumulative_return_bar_chart: Path
    ma_chart: Path
    final_returns: dict[str, float]


@dataclass(frozen=True)
class Task3Result:
    stock: StockInfo
    signal_data_file: Path
    metrics_file: Path
    ma_chart: Path
    signal_chart: Path
    cumulative_return_chart: Path
    buy_signals: int
    sell_signals: int
    stock_cumulative_return: float
    strategy_cumulative_return: float
    max_drawdown: float
    completed_trades: int
    profitable_trades: int
    analysis_text: list[str]


@dataclass(frozen=True)
class AnalysisBundle:
    task1: Task1Result
    task2: Task2Result
    task3: Task3Result
    master_summary_file: Path


def _slugify_stock(stock: StockInfo) -> str:
    return f"{stock.ts_code}_{stock.name}".replace(".", "_")


def _save_figure(fig: plt.Figure, path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=200, bbox_inches="tight")
    plt.close(fig)
    return path


def _calculate_max_drawdown(cumulative_series: pd.Series) -> float:
    wealth = (1 + cumulative_series.fillna(0)).cummax()
    drawdown = (1 + cumulative_series.fillna(0)) / wealth - 1
    return float(drawdown.min())


def _count_completed_trades(df: pd.DataFrame) -> tuple[int, int]:
    buy_dates = df.index[df["signal"] == 1].tolist()
    sell_dates = df.index[df["signal"] == -1].tolist()
    completed = 0
    profitable = 0
    sell_pointer = 0

    for buy_date in buy_dates:
        while sell_pointer < len(sell_dates) and sell_dates[sell_pointer] <= buy_date:
            sell_pointer += 1
        if sell_pointer >= len(sell_dates):
            break
        sell_date = sell_dates[sell_pointer]
        buy_price = float(df.loc[buy_date, "close"])
        sell_price = float(df.loc[sell_date, "close"])
        completed += 1
        if sell_price > buy_price:
            profitable += 1
        sell_pointer += 1

    return completed, profitable


class TushareAnalyzer:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.pro = ts.pro_api(settings.token)

    def run_all(self) -> AnalysisBundle:
        task1 = self.run_task1()
        task2 = self.run_task2()
        task3 = self.run_task3()
        master_summary = self._write_master_summary(task1, task2, task3)
        return AnalysisBundle(
            task1=task1,
            task2=task2,
            task3=task3,
            master_summary_file=master_summary,
        )

    def fetch_daily_data(self, stock: StockInfo, start_date: str, end_date: str) -> pd.DataFrame:
        frame = self.pro.daily(ts_code=stock.ts_code, start_date=start_date, end_date=end_date)
        if frame.empty:
            raise ValueError(
                f"Tushare 未返回数据：{stock.name} ({stock.ts_code}) {start_date} - {end_date}"
            )
        time.sleep(0.2)
        return frame

    @staticmethod
    def clean_daily_data(frame: pd.DataFrame) -> tuple[pd.DataFrame, int, int]:
        cleaned = frame.copy()
        duplicate_rows = int(cleaned.duplicated(subset=["trade_date"]).sum())
        cleaned = cleaned.drop_duplicates(subset=["trade_date"]).copy()
        cleaned["trade_date"] = pd.to_datetime(cleaned["trade_date"], format="%Y%m%d")
        cleaned = cleaned.sort_values("trade_date").reset_index(drop=True)
        missing_cells = int(cleaned.isna().sum().sum())
        return cleaned, duplicate_rows, missing_cells

    @staticmethod
    def add_indicators(frame: pd.DataFrame) -> pd.DataFrame:
        enriched = frame.copy()
        enriched["daily_return"] = enriched["close"].pct_change().fillna(0)
        enriched["cumulative_return"] = (1 + enriched["daily_return"]).cumprod() - 1
        enriched["ma5"] = enriched["close"].rolling(window=5).mean()
        enriched["ma20"] = enriched["close"].rolling(window=20).mean()
        enriched["month"] = enriched["trade_date"].dt.to_period("M").astype(str)
        return enriched

    def run_task1(self) -> Task1Result:
        stock = self.settings.task1_stock
        raw = self.fetch_daily_data(stock, self.settings.task1_start, self.settings.task1_end)
        cleaned, duplicate_rows, missing_cells = self.clean_daily_data(raw)
        enriched = self.add_indicators(cleaned)

        data_file = DATA_DIR / f"task1_{_slugify_stock(stock)}_cleaned.csv"
        monthly_file = DATA_DIR / f"task1_{_slugify_stock(stock)}_monthly_mean.csv"
        summary_file = DATA_DIR / f"task1_{_slugify_stock(stock)}_summary.json"
        enriched.to_csv(data_file, index=False, encoding="utf-8-sig")

        monthly_mean = (
            enriched.groupby("month", as_index=False)["close"].mean().rename(
                columns={"close": "monthly_close_mean"}
            )
        )
        monthly_mean.to_csv(monthly_file, index=False, encoding="utf-8-sig")

        volume_chart = self._plot_task1_volume(stock, enriched)
        monthly_chart = self._plot_task1_monthly_mean(stock, monthly_mean)

        summary = {
            "stock_name": stock.name,
            "stock_code": stock.ts_code,
            "total_rows": int(len(enriched)),
            "duplicate_rows": duplicate_rows,
            "missing_cells": missing_cells,
            "closing_price_mean": float(enriched["close"].mean()),
            "closing_price_std": float(enriched["close"].std(ddof=1)),
            "volume_mean": float(enriched["vol"].mean()),
            "highest_close": float(enriched["close"].max()),
            "lowest_close": float(enriched["close"].min()),
        }
        summary_file.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")

        return Task1Result(
            stock=stock,
            cleaned_data_file=data_file,
            monthly_mean_file=monthly_file,
            volume_chart=volume_chart,
            monthly_chart=monthly_chart,
            summary_file=summary_file,
            total_rows=summary["total_rows"],
            duplicate_rows=duplicate_rows,
            missing_cells=missing_cells,
            closing_price_mean=summary["closing_price_mean"],
            closing_price_std=summary["closing_price_std"],
            volume_mean=summary["volume_mean"],
            highest_close=summary["highest_close"],
            lowest_close=summary["lowest_close"],
        )

    def run_task2(self) -> Task2Result:
        combined_frames: list[pd.DataFrame] = []
        final_returns: dict[str, float] = {}

        for stock in self.settings.task2_stocks:
            raw = self.fetch_daily_data(stock, self.settings.task2_start, self.settings.task2_end)
            cleaned, _, _ = self.clean_daily_data(raw)
            enriched = self.add_indicators(cleaned)
            enriched["stock_name"] = stock.name
            enriched["industry"] = stock.industry
            final_returns[f"{stock.name} ({stock.ts_code})"] = float(enriched["cumulative_return"].iloc[-1])
            combined_frames.append(enriched)

            stock_file = DATA_DIR / f"task2_{_slugify_stock(stock)}_cleaned.csv"
            enriched.to_csv(stock_file, index=False, encoding="utf-8-sig")

        combined = pd.concat(combined_frames, ignore_index=True)
        combined_data_file = DATA_DIR / "task2_combined_stock_data.csv"
        combined.to_csv(combined_data_file, index=False, encoding="utf-8-sig")

        final_return_frame = pd.DataFrame(
            {
                "stock": list(final_returns.keys()),
                "final_cumulative_return": list(final_returns.values()),
            }
        ).sort_values("final_cumulative_return", ascending=False)
        final_return_file = DATA_DIR / "task2_final_cumulative_returns.csv"
        final_return_frame.to_csv(final_return_file, index=False, encoding="utf-8-sig")

        cumulative_return_bar_chart = self._plot_task2_cumulative_return_bar(final_return_frame)
        ma_target = self.settings.task3_stock
        ma_frame = combined.loc[combined["ts_code"] == ma_target.ts_code].copy()
        ma_chart = self._plot_ma_chart(
            stock=ma_target,
            frame=ma_frame,
            path=CHARTS_DIR / f"task2_{_slugify_stock(ma_target)}_ma_chart.png",
            title=f"题目二：{ma_target.name} 收盘价与 5 日、20 日均线",
        )

        return Task2Result(
            stocks=self.settings.task2_stocks,
            combined_data_file=combined_data_file,
            final_return_file=final_return_file,
            cumulative_return_bar_chart=cumulative_return_bar_chart,
            ma_chart=ma_chart,
            final_returns=final_returns,
        )

    def run_task3(self) -> Task3Result:
        stock = self.settings.task3_stock
        raw = self.fetch_daily_data(stock, self.settings.task3_start, self.settings.task3_end)
        cleaned, _, _ = self.clean_daily_data(raw)
        enriched = self.add_indicators(cleaned)
        enriched = self._build_signals(enriched)

        signal_data_file = DATA_DIR / f"task3_{_slugify_stock(stock)}_signals.csv"
        metrics_file = DATA_DIR / f"task3_{_slugify_stock(stock)}_metrics.json"
        enriched.to_csv(signal_data_file, index=False, encoding="utf-8-sig")

        ma_chart = self._plot_ma_chart(
            stock=stock,
            frame=enriched,
            path=CHARTS_DIR / f"task3_{_slugify_stock(stock)}_ma_chart.png",
            title=f"题目三：{stock.name} 收盘价与均线",
        )
        signal_chart = self._plot_signal_chart(stock, enriched)
        cumulative_return_chart = self._plot_task3_cumulative_return_chart(stock, enriched)

        buy_signals = int((enriched["signal"] == 1).sum())
        sell_signals = int((enriched["signal"] == -1).sum())
        stock_return = float(enriched["cumulative_return"].iloc[-1])
        strategy_return = float(enriched["strategy_cumulative_return"].iloc[-1])
        max_drawdown = _calculate_max_drawdown(enriched["strategy_cumulative_return"])
        completed_trades, profitable_trades = _count_completed_trades(enriched.set_index("trade_date"))

        analysis_text = self._build_strategy_analysis(
            stock_return=stock_return,
            strategy_return=strategy_return,
            buy_signals=buy_signals,
            sell_signals=sell_signals,
            max_drawdown=max_drawdown,
            completed_trades=completed_trades,
            profitable_trades=profitable_trades,
        )

        metrics = {
            "stock_name": stock.name,
            "stock_code": stock.ts_code,
            "start_date": self.settings.task3_start,
            "end_date": self.settings.task3_end,
            "buy_signals": buy_signals,
            "sell_signals": sell_signals,
            "stock_cumulative_return": stock_return,
            "strategy_cumulative_return": strategy_return,
            "max_drawdown": max_drawdown,
            "completed_trades": completed_trades,
            "profitable_trades": profitable_trades,
            "analysis_text": analysis_text,
        }
        metrics_file.write_text(json.dumps(metrics, ensure_ascii=False, indent=2), encoding="utf-8")

        return Task3Result(
            stock=stock,
            signal_data_file=signal_data_file,
            metrics_file=metrics_file,
            ma_chart=ma_chart,
            signal_chart=signal_chart,
            cumulative_return_chart=cumulative_return_chart,
            buy_signals=buy_signals,
            sell_signals=sell_signals,
            stock_cumulative_return=stock_return,
            strategy_cumulative_return=strategy_return,
            max_drawdown=max_drawdown,
            completed_trades=completed_trades,
            profitable_trades=profitable_trades,
            analysis_text=analysis_text,
        )

    @staticmethod
    def _build_signals(frame: pd.DataFrame) -> pd.DataFrame:
        signal_frame = frame.copy()
        buy_cross = (signal_frame["ma5"] > signal_frame["ma20"]) & (
            signal_frame["ma5"].shift(1) <= signal_frame["ma20"].shift(1)
        )
        sell_cross = (signal_frame["ma5"] < signal_frame["ma20"]) & (
            signal_frame["ma5"].shift(1) >= signal_frame["ma20"].shift(1)
        )

        signal_frame["signal"] = 0
        signal_frame.loc[buy_cross, "signal"] = 1
        signal_frame.loc[sell_cross, "signal"] = -1

        signal_frame["position"] = np.nan
        signal_frame.loc[buy_cross, "position"] = 1
        signal_frame.loc[sell_cross, "position"] = 0
        signal_frame["position"] = signal_frame["position"].ffill().fillna(0)
        signal_frame["strategy_return"] = (
            signal_frame["position"].shift(1).fillna(0) * signal_frame["daily_return"]
        )
        signal_frame["strategy_cumulative_return"] = (
            1 + signal_frame["strategy_return"].fillna(0)
        ).cumprod() - 1
        return signal_frame

    @staticmethod
    def _build_strategy_analysis(
        stock_return: float,
        strategy_return: float,
        buy_signals: int,
        sell_signals: int,
        max_drawdown: float,
        completed_trades: int,
        profitable_trades: int,
    ) -> list[str]:
        outperform = strategy_return - stock_return
        if completed_trades > 0:
            win_rate = profitable_trades / completed_trades
        else:
            win_rate = 0.0

        performance_text = (
            f"研究区间内共出现 {buy_signals} 次买入信号、{sell_signals} 次卖出信号，"
            f"完成 {completed_trades} 笔完整交易，盈利交易占比约为 {win_rate:.2%}。"
        )
        comparison_text = (
            f"股票自身累计收益率为 {stock_return:.2%}，均线策略累计收益率为 {strategy_return:.2%}，"
            f"两者差值为 {outperform:.2%}。"
        )
        risk_text = (
            f"策略累计收益序列的最大回撤约为 {max_drawdown:.2%}，"
            "说明在震荡行情中仍可能出现较明显回撤。"
        )
        strengths_text = (
            "该规则优点是逻辑简单、易于实现，能够在趋势形成后跟随价格方向，"
            "适合用作技术分析入门示例。"
        )
        limitation_text = (
            "局限在于均线信号具有滞后性，横盘震荡时容易频繁触发买卖，"
            "且未考虑交易成本、滑点和仓位管理。"
        )
        return [performance_text, comparison_text, risk_text, strengths_text, limitation_text]

    def _plot_task1_volume(self, stock: StockInfo, frame: pd.DataFrame) -> Path:
        fig, ax = plt.subplots(figsize=(14, 6))
        ax.bar(frame["trade_date"], frame["vol"], color="#2E86AB", width=1.5)
        ax.set_title(f"题目一：{stock.name} 2025 年每日成交量")
        ax.set_xlabel("交易日期")
        ax.set_ylabel("成交量（手）")
        ax.grid(axis="y", alpha=0.3)
        ax.xaxis.set_major_locator(mdates.MonthLocator(interval=1))
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m"))
        fig.autofmt_xdate()
        return _save_figure(fig, CHARTS_DIR / f"task1_{_slugify_stock(stock)}_volume.png")

    def _plot_task1_monthly_mean(self, stock: StockInfo, monthly_mean: pd.DataFrame) -> Path:
        fig, ax = plt.subplots(figsize=(12, 5))
        ax.plot(
            monthly_mean["month"],
            monthly_mean["monthly_close_mean"],
            marker="o",
            linewidth=2.2,
            color="#D35400",
        )
        ax.set_title(f"题目一：{stock.name} 每月收盘价均值")
        ax.set_xlabel("月份")
        ax.set_ylabel("月均收盘价")
        ax.grid(alpha=0.3)
        plt.xticks(rotation=45)
        return _save_figure(fig, CHARTS_DIR / f"task1_{_slugify_stock(stock)}_monthly_mean.png")

    @staticmethod
    def _plot_ma_chart(stock: StockInfo, frame: pd.DataFrame, path: Path, title: str) -> Path:
        fig, ax = plt.subplots(figsize=(14, 6))
        ax.plot(frame["trade_date"], frame["close"], label="收盘价", color="#1F618D", linewidth=1.8)
        ax.plot(frame["trade_date"], frame["ma5"], label="5 日均线", color="#F39C12", linewidth=1.5)
        ax.plot(frame["trade_date"], frame["ma20"], label="20 日均线", color="#27AE60", linewidth=1.5)
        ax.set_title(title)
        ax.set_xlabel("交易日期")
        ax.set_ylabel("价格")
        ax.grid(alpha=0.3)
        ax.legend()
        ax.xaxis.set_major_locator(mdates.MonthLocator(interval=2))
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m"))
        fig.autofmt_xdate()
        return _save_figure(fig, path)

    @staticmethod
    def _plot_task2_cumulative_return_bar(final_return_frame: pd.DataFrame) -> Path:
        fig, ax = plt.subplots(figsize=(10, 6))
        colors = ["#27AE60" if value >= 0 else "#C0392B" for value in final_return_frame["final_cumulative_return"]]
        ax.bar(final_return_frame["stock"], final_return_frame["final_cumulative_return"], color=colors)
        ax.set_title("题目二：三只股票最终累计收益率对比")
        ax.set_xlabel("股票")
        ax.set_ylabel("最终累计收益率")
        ax.grid(axis="y", alpha=0.3)
        plt.xticks(rotation=15)

        for idx, value in enumerate(final_return_frame["final_cumulative_return"]):
            ax.text(idx, value, f"{value:.2%}", ha="center", va="bottom" if value >= 0 else "top")

        return _save_figure(fig, CHARTS_DIR / "task2_cumulative_return_comparison.png")

    def _plot_signal_chart(self, stock: StockInfo, frame: pd.DataFrame) -> Path:
        fig, ax = plt.subplots(figsize=(14, 6))
        ax.plot(frame["trade_date"], frame["close"], label="收盘价", color="#1F618D", linewidth=1.8)
        ax.plot(frame["trade_date"], frame["ma5"], label="5 日均线", color="#F39C12", linewidth=1.2)
        ax.plot(frame["trade_date"], frame["ma20"], label="20 日均线", color="#27AE60", linewidth=1.2)

        buy_points = frame.loc[frame["signal"] == 1]
        sell_points = frame.loc[frame["signal"] == -1]
        ax.scatter(
            buy_points["trade_date"],
            buy_points["close"],
            label="买入信号",
            marker="^",
            s=90,
            color="#C0392B",
        )
        ax.scatter(
            sell_points["trade_date"],
            sell_points["close"],
            label="卖出信号",
            marker="v",
            s=90,
            color="#8E44AD",
        )
        ax.set_title(f"题目三：{stock.name} 买卖信号标注图")
        ax.set_xlabel("交易日期")
        ax.set_ylabel("价格")
        ax.grid(alpha=0.3)
        ax.legend()
        ax.xaxis.set_major_locator(mdates.MonthLocator(interval=2))
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m"))
        fig.autofmt_xdate()
        return _save_figure(fig, CHARTS_DIR / f"task3_{_slugify_stock(stock)}_signal_chart.png")

    def _plot_task3_cumulative_return_chart(self, stock: StockInfo, frame: pd.DataFrame) -> Path:
        fig, ax = plt.subplots(figsize=(14, 6))
        ax.plot(
            frame["trade_date"],
            frame["cumulative_return"],
            label="股票累计收益率",
            color="#1F618D",
            linewidth=1.8,
        )
        ax.plot(
            frame["trade_date"],
            frame["strategy_cumulative_return"],
            label="策略累计收益率",
            color="#C0392B",
            linewidth=1.8,
        )
        ax.set_title(f"题目三：{stock.name} 累计收益率变化图")
        ax.set_xlabel("交易日期")
        ax.set_ylabel("累计收益率")
        ax.grid(alpha=0.3)
        ax.legend()
        ax.xaxis.set_major_locator(mdates.MonthLocator(interval=2))
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m"))
        fig.autofmt_xdate()
        return _save_figure(fig, CHARTS_DIR / f"task3_{_slugify_stock(stock)}_cumulative_return.png")

    def _write_master_summary(
        self, task1: Task1Result, task2: Task2Result, task3: Task3Result
    ) -> Path:
        summary = {
            "project_title": self.settings.project_title,
            "task1": {
                "stock": task1.stock.name,
                "stock_code": task1.stock.ts_code,
                "total_rows": task1.total_rows,
                "duplicate_rows": task1.duplicate_rows,
                "missing_cells": task1.missing_cells,
                "closing_price_mean": task1.closing_price_mean,
                "closing_price_std": task1.closing_price_std,
                "volume_mean": task1.volume_mean,
                "highest_close": task1.highest_close,
                "lowest_close": task1.lowest_close,
            },
            "task2": {
                "final_returns": task2.final_returns,
            },
            "task3": {
                "stock": task3.stock.name,
                "stock_code": task3.stock.ts_code,
                "buy_signals": task3.buy_signals,
                "sell_signals": task3.sell_signals,
                "stock_cumulative_return": task3.stock_cumulative_return,
                "strategy_cumulative_return": task3.strategy_cumulative_return,
                "max_drawdown": task3.max_drawdown,
                "completed_trades": task3.completed_trades,
                "profitable_trades": task3.profitable_trades,
                "analysis_text": task3.analysis_text,
            },
        }
        path = DATA_DIR / "analysis_master_summary.json"
        path.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
        return path

from __future__ import annotations

from src.analysis import TushareAnalyzer
from src.config import load_settings
from src.report_builder import ReportBuilder


def main() -> None:
    settings = load_settings()
    if not settings.token:
        raise SystemExit("Missing TUSHARE_TOKEN. Please configure it in .env first.")

    analyzer = TushareAnalyzer(settings)
    bundle = analyzer.run_all()

    report_builder = ReportBuilder(settings, bundle)
    report_path = report_builder.build()

    print(f"{settings.project_title} 已完成。")
    print(f"Word 报告：{report_path}")
    print(f"汇总结果：{bundle.master_summary_file}")


if __name__ == "__main__":
    main()

"""Command-line entry point for the reusable automated reporting package."""

from pathlib import Path
import argparse
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.reporting import ReportApplication


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate the transaction analysis PDF report.")
    parser.add_argument(
        "--data",
        type=Path,
        default=PROJECT_ROOT / "03-Data cleaning" / "clean_data.csv",
        help="Combined CSV input (default: 03-Data cleaning/clean_data.csv)",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=PROJECT_ROOT / "05-Report",
        help="Directory for the PDF and chart images",
    )
    parser.add_argument("--report-name", default="project_report.pdf", help="PDF output filename")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        application = ReportApplication(args.data, args.output_dir, args.report_name)
        application.run()
        return 0
    except (FileNotFoundError, ValueError, RuntimeError, OSError) as error:
        print(f"Report generation failed: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

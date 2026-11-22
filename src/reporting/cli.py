"""Command-line entry point for automated report generation."""

import argparse
from pathlib import Path
import sys

from .application import ReportApplication

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_DATA_FILE = PROJECT_ROOT / "03-Data cleaning" / "clean_data.csv"
DEFAULT_OUTPUT_DIR = PROJECT_ROOT / "05-Report"


def build_parser() -> argparse.ArgumentParser:
    """Create the report command-line argument parser."""
    parser = argparse.ArgumentParser(
        description="Generate the transaction analysis PDF report."
    )
    parser.add_argument(
        "--data",
        type=Path,
        default=DEFAULT_DATA_FILE,
        help="Combined CSV input (default: 03-Data cleaning/clean_data.csv)",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help="Directory for the PDF and chart images",
    )
    parser.add_argument(
        "--report-name",
        default="project_report.pdf",
        help="PDF output filename",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    """Run report generation, returning a process exit status."""
    args = build_parser().parse_args(argv)
    try:
        application = ReportApplication(
            args.data,
            args.output_dir,
            args.report_name,
        )
        application.run()
        return 0
    except (FileNotFoundError, ValueError, RuntimeError, OSError) as error:
        print(f"Report generation failed: {error}", file=sys.stderr)
        return 1

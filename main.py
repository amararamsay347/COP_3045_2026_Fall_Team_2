"""Main entry point for data preparation, EDA, and automated reporting."""

from pathlib import Path
import subprocess
import sys

PROJECT_ROOT = Path(__file__).resolve().parent

WORKFLOW_STEPS = (
    "src/main.py",
    "src/summary_statistics.py",
    "04-EDA/graphical_eda.py",
    "05-Report/generate_report.py",
)


def main() -> int:
    """Run the complete analytical and reporting workflow in order."""
    for step in WORKFLOW_STEPS:
        step_path = PROJECT_ROOT / step
        if not step_path.is_file():
            print(f"Workflow script not found: {step_path}", file=sys.stderr)
            return 1

        print(f"=== Running {step} ===", flush=True)
        try:
            subprocess.run(
                [sys.executable, str(step_path)],
                cwd=PROJECT_ROOT,
                check=True,
            )
        except subprocess.CalledProcessError as error:
            print(
                f"Workflow stopped: {step} exited with status {error.returncode}.",
                file=sys.stderr,
            )
            return error.returncode or 1

    print("Done. Report: 05-Report/project_report.pdf")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

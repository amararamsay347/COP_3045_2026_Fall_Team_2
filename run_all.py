from pathlib import Path
import subprocess
import sys


PROJECT_ROOT = Path(__file__).resolve().parent
STEPS = (
    "src/main.py",
    "src/summary_statistics.py",
    "04-EDA/graphical_eda.py",
    "05-Report/generate_report.py",
)


def main() -> None:
    for step in STEPS:
        print(f"=== Running {step} ===", flush=True)
        subprocess.run(
            [sys.executable, str(PROJECT_ROOT / step)],
            cwd=PROJECT_ROOT,
            check=True,
        )

    print("Done. Report: 05-Report/project_report.pdf")


if __name__ == "__main__":
    main()

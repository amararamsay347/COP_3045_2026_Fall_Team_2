import subprocess
import sys

from src.paths import PROJECT_DIR, REPORT_FILE


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
            [sys.executable, str(PROJECT_DIR / step)],
            cwd=PROJECT_DIR,
            check=True,
        )

    print(f"Done. Report: {REPORT_FILE.relative_to(PROJECT_DIR).as_posix()}")


if __name__ == "__main__":
    main()

from pathlib import Path
import importlib.util
import os
import shutil
import subprocess
import sys


PROJECT_ROOT = Path(__file__).resolve().parent
STEPS = (
    "src/main.py",
    "src/summary_statistics.py",
    "04-EDA/graphical_eda.py",
    "05-Report/generate_report.py",
)
ENVIRONMENT_NAME = "cop3045"
RUNNER_ENV_MARKER = "COP3045_RUNNER_ENV"
REQUIRED_MODULES = {
    "pandas": "pandas",
    "matplotlib": "matplotlib",
    "seaborn": "seaborn",
    "fpdf": "fpdf2",
}


def _run_in_project_environment() -> bool:
    if os.environ.get(RUNNER_ENV_MARKER) == "1":
        return False

    if os.environ.get("CONDA_DEFAULT_ENV") == ENVIRONMENT_NAME:
        return False

    conda = shutil.which("conda")
    if conda is None:
        raise RuntimeError(
            "Conda is required. Create the project environment with "
            "'conda env create -f environment.yml', activate it with "
            "'conda activate cop3045', then rerun this script."
        )

    child_environment = os.environ.copy()
    child_environment[RUNNER_ENV_MARKER] = "1"
    subprocess.run(
        [
            conda,
            "run",
            "--no-capture-output",
            "-n",
            ENVIRONMENT_NAME,
            "python",
            str(Path(__file__).resolve()),
        ],
        cwd=PROJECT_ROOT,
        env=child_environment,
        check=True,
    )
    return True


def _check_dependencies() -> None:
    missing = [
        package
        for module, package in REQUIRED_MODULES.items()
        if importlib.util.find_spec(module) is None
    ]
    if missing:
        raise RuntimeError(
            "The cop3045 environment is missing required packages: "
            + ", ".join(missing)
            + ". Update it with 'conda env update -f environment.yml --prune'."
        )


def main() -> None:
    if _run_in_project_environment():
        return

    _check_dependencies()

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

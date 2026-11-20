"""Backward-compatible launcher for the application entry point."""

from main import main as run_application


def main() -> int:
    """Run the same complete workflow as ``python main.py``."""
    return run_application()


if __name__ == "__main__":
    raise SystemExit(main())

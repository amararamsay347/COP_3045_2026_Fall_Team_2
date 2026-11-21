"""Locate and read raw transaction datasets."""

from pathlib import Path

import pandas as pd


def find_dataset(
    expected_path: Path,
    alternate_path: Path
) -> Path:
    """Locate a dataset using its primary or alternate file path."""
    for path in (expected_path, alternate_path):
        if path.is_file():
            return path
    raise FileNotFoundError(
        f"Dataset not found. Place {expected_path.name} at {expected_path} "
        f"or {alternate_path}."
    )


def load_csv(
    file_path: str | Path,
    columns: list[str] | None = None,
    nrows: int | None = None
) -> pd.DataFrame:
    """Load a CSV file with validation and informative error messages."""

    file_path = Path(file_path)

    if not file_path.is_file():
        raise FileNotFoundError(
            f"Dataset file not found: {file_path}"
        )

    try:
        df = pd.read_csv(
            file_path,
            usecols=columns,
            nrows=nrows
        )

    except pd.errors.EmptyDataError as error:
        raise ValueError(
            f"The CSV file is empty: {file_path}"
        ) from error

    except (OSError, pd.errors.ParserError) as error:
        raise ValueError(
            f"Unable to read CSV file {file_path}: {error}"
        ) from error

    except ValueError as error:
        raise ValueError(
            f"Invalid or missing columns in {file_path}: {error}"
        ) from error

    return df

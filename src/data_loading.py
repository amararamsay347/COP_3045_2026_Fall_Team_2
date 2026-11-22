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


TRANSACTION_COLUMNS = {
    "dataset_source",
    "label_type",
    "transaction_category",
    "transaction_amount",
    "currency",
    "is_suspicious",
}


def load_combined_transactions(
    path: Path, *, extra_columns: tuple[str, ...] = ()
) -> pd.DataFrame:
    """Read the shared analytics schema and validate source and label values."""
    if not path.is_file():
        raise FileNotFoundError(
            f"Combined dataset not found: {path}. Run python -m src.main to create it."
        )

    columns = TRANSACTION_COLUMNS.union(extra_columns)
    try:
        transactions = pd.read_csv(
            path,
            usecols=lambda column: column in columns,
            dtype=dict.fromkeys(
                ("dataset_source", "label_type", "transaction_category", "currency"),
                "category",
            ),
            low_memory=False,
        )
    except (OSError, ValueError) as error:
        raise ValueError(f"Unable to read combined dataset {path}: {error}") from error

    missing = columns.difference(transactions.columns)
    if missing:
        raise ValueError(f"{path} is missing columns: {', '.join(sorted(missing))}.")
    if transactions.empty:
        raise ValueError(f"{path} has no transaction rows.")

    labels = pd.to_numeric(transactions["is_suspicious"], errors="coerce")
    invalid_count = int((~labels.isin([0, 1])).sum())
    if invalid_count:
        raise ValueError(
            f"{path}: is_suspicious must be 0 or 1. "
            f"Found {invalid_count:,} missing or invalid labels."
        )

    sources = transactions["dataset_source"]
    label_types = transactions["label_type"]
    valid_pairs = (
        (sources.eq("PAYSim") & label_types.eq("fraud"))
        | (sources.eq("IBM") & label_types.eq("laundering"))
    )
    if not valid_pairs.all():
        raise ValueError(f"{path}: expected PAYSim/fraud or IBM/laundering labels.")

    amounts = transactions["transaction_amount"]
    numeric_amounts = pd.to_numeric(amounts, errors="coerce")
    if ((amounts.notna() & numeric_amounts.isna()) | numeric_amounts.isin(
        [float("inf"), float("-inf")]
    )).any():
        raise ValueError(f"{path}: transaction_amount must contain finite numbers or blanks.")

    transactions["is_suspicious"] = labels.astype("int8")
    transactions["transaction_amount"] = numeric_amounts
    return transactions

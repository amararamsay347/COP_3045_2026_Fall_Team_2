"""Data loading and validation for automated reports."""

from pathlib import Path
import pandas as pd

REQUIRED_COLUMNS = (
    "transaction_amount",
    "currency",
    "transaction_category",
    "dataset_source",
    "label_type",
    "is_suspicious",
)


def load_combined_data(data_file: Path) -> tuple[pd.DataFrame, int]:
    """Load and normalize a combined transaction dataset.

    Raises:
        FileNotFoundError: If the dataset does not exist.
        ValueError: If required fields or transaction values are missing or invalid.
    """
    data_file = Path(data_file)
    if not data_file.is_file():
        raise FileNotFoundError(
            f"Combined dataset not found: {data_file}. "
            "Run 'python src/main.py' from the project root first."
        )

    try:
        total_columns = len(pd.read_csv(data_file, nrows=0).columns)
        frame = pd.read_csv(
            data_file,
            usecols=list(REQUIRED_COLUMNS),
            low_memory=False,
        )
    except (OSError, pd.errors.ParserError, ValueError) as error:
        raise ValueError(f"Unable to read combined dataset {data_file}: {error}") from error

    missing = set(REQUIRED_COLUMNS).difference(frame.columns)
    if missing:
        raise ValueError("Combined dataset missing columns: " + ", ".join(sorted(missing)))
    if frame.empty:
        raise ValueError("Combined dataset contains no transaction rows.")

    frame["transaction_amount"] = pd.to_numeric(frame["transaction_amount"], errors="coerce")
    frame["is_suspicious"] = pd.to_numeric(frame["is_suspicious"], errors="coerce")
    if not frame["is_suspicious"].dropna().isin([0, 1]).all():
        raise ValueError("is_suspicious must contain only 0 and 1 values.")

    frame["currency"] = frame["currency"].fillna("N/A").astype(str)
    frame["dataset_source"] = frame["dataset_source"].astype(str).replace({"PAYSim": "PaySim"})
    frame["transaction_category"] = frame["transaction_category"].fillna("Unknown").astype(str)
    frame["label_type"] = frame["label_type"].fillna("Unknown").astype(str)
    frame["is_suspicious"] = frame["is_suspicious"].fillna(0).astype("int8")

    return frame, total_columns

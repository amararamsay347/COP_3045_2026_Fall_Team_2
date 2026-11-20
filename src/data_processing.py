import pandas as pd
from pathlib import Path


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

    except ValueError as error:
        raise ValueError(
            f"Invalid or missing columns in {file_path}: {error}"
        ) from error

    except (OSError, pd.errors.ParserError) as error:
        raise ValueError(
            f"Unable to read CSV file {file_path}: {error}"
        ) from error

    return df


def display_dataset_info(df: pd.DataFrame, dataset_name: str) -> None:
    """Display basic information and data quality statistics for a dataset."""

    print(f"\n{'=' * 60}")
    print(f"DATASET: {dataset_name}")
    print(f"{'=' * 60}")

    print("\nFirst 5 rows:")
    print(df.head())

    print("\nColumns:")
    print(df.columns)

    print("\nData types:")
    print(df.dtypes)

    print("\nMissing values:")
    print(df.isna().sum())

    print("\nDuplicates:")
    print(df.duplicated().sum())

    print("\nShape:")
    print(df.shape)

# Review a sample of the PAYSim data to inspect schema, types, missing values, and duplicates.
def inspect_paysim(file_path: str | Path) -> None:
    """Inspect a sample of PaySim transactions for structure and data quality."""

    paysim = load_csv(file_path, nrows=5000)

    display_dataset_info(paysim, "PAYSim")


# Inspect each IBM CSV file in a folder and print a summary of its structure and data quality.
def inspect_ibm(folder_path: str | Path) -> None:
    """Inspect CSV files in an IBM dataset folder for data quality."""

    folder = Path(folder_path)

    if not folder.is_dir():
        raise NotADirectoryError(
            f"IBM dataset folder not found: {folder}"
        )

    files = sorted(folder.glob("*.csv"))

    if not files:
        raise ValueError(
            f"No CSV files found in: {folder}"
        )

    for file in files:
        df = load_csv(file, nrows=5000)

        display_dataset_info(df, file.name)


# Keep only the relevant PAYSim fields and create derived features useful for fraud detection.
def clean_paysim(file_path: str | Path) -> pd.DataFrame:
    """Load and clean PaySim transactions and create derived features."""
    # Select the columns needed for analysis and reduce memory use for the dataset.
    columns = ["step",
               "type",
               "amount",
               "oldbalanceOrg",
               "newbalanceOrig",
               "oldbalanceDest",
               "newbalanceDest",
               "isFraud"]

    df = load_csv(file_path, columns=columns)

    # Standardize transaction labels so the values are consistent and easy to compare.
    df["type"] = df["type"].str.strip().str.upper()

    # Add the hour of the transaction to help detect time-based fraud patterns.
    df["hour"] = df["step"] % 24

    # Calculate how much each account balance changed during a transaction.
    df["origin_balance_change"] = df["newbalanceOrig"] - df["oldbalanceOrg"]

    # Measure the recipient-side balance shift to reveal suspicious transfers.
    df["destination_balance_change"] = df["newbalanceDest"] - df["oldbalanceDest"]

    return df


# Select the primary IBM fields and normalize values so the financial records are easier to analyze.
def clean_ibm(file_path: str | Path) -> pd.DataFrame:
    """Load and clean IBM transactions and create derived features."""

    # Keep only the columns most relevant to laundering detection and payment pattern analysis.
    columns = [
        "Timestamp",
        "From Bank",
        "To Bank",
        "Amount Received",
        "Receiving Currency",
        "Amount Paid",
        "Payment Currency",
        "Payment Format",
        "Is Laundering"
    ]

    df = load_csv(file_path, columns=columns)

    # Convert timestamps to a proper datetime type for time-based analysis.
    try:
        df["Timestamp"] = pd.to_datetime(
            df["Timestamp"],
            errors="raise"
        )

    except (ValueError, TypeError) as error:
        raise ValueError(
            f"Invalid timestamps in IBM dataset: {error}"
        ) from error

    # Normalize currency strings to uppercase for consistent comparisons.
    df["Receiving Currency"] = df["Receiving Currency"].str.strip().str.upper()
    df["Payment Currency"] = df["Payment Currency"].str.strip().str.upper()
    df["Payment Format"] = df["Payment Format"].str.strip().str.upper()

    # Add derived time and relationship features to support pattern analysis.
    df["hour"] = df["Timestamp"].dt.hour
    df["Same Bank"] = df["From Bank"] == df["To Bank"]

    return df


def combine_datasets(paysim: pd.DataFrame, ibm: pd.DataFrame) -> pd.DataFrame:
    """Combine cleaned PaySim and IBM datasets for shared fraud analysis."""
    # Add comparable analysis fields while preserving each dataset's original columns.
    paysim_analytics = paysim.copy()
    paysim_analytics["dataset_source"] = "PAYSim"
    paysim_analytics["transaction_amount"] = paysim["amount"]
    paysim_analytics["currency"] = pd.NA
    paysim_analytics["transaction_category"] = paysim["type"]
    paysim_analytics["is_suspicious"] = paysim["isFraud"]
    paysim_analytics["label_type"] = "fraud"

    ibm_analytics = ibm.copy()
    ibm_analytics["dataset_source"] = "IBM"
    ibm_analytics["transaction_amount"] = ibm["Amount Received"]
    ibm_analytics["currency"] = ibm["Receiving Currency"]
    ibm_analytics["transaction_category"] = ibm["Payment Format"]
    ibm_analytics["is_suspicious"] = ibm["Is Laundering"]
    ibm_analytics["label_type"] = "laundering"

    return pd.concat(
        [paysim_analytics, ibm_analytics],
        ignore_index=True,
        sort=False,
    )


class TransactionDataProcessor:
    """Manage the inspection, cleaning, and combination of transaction datasets."""

    def __init__(
        self,
        paysim_path: str | Path,
        ibm_path: str | Path
    ) -> None:
        """Initialize the processor with dataset file paths."""

        self._paysim_path = Path(paysim_path)
        self._ibm_path = Path(ibm_path)

        self._paysim_data = None
        self._ibm_data = None

    def inspect_data(self) -> None:
        """Inspect the PaySim and IBM transaction datasets."""

        inspect_paysim(self._paysim_path)
        inspect_ibm(self._ibm_path.parent)

    def clean_data(self) -> None:
        """Clean both datasets and store the results."""

        self._paysim_data = clean_paysim(self._paysim_path)
        self._ibm_data = clean_ibm(self._ibm_path)

    def get_cleaned_data(self) -> tuple[pd.DataFrame, pd.DataFrame]:
        """Return copies of the cleaned PaySim and IBM datasets."""

        if self._paysim_data is None or self._ibm_data is None:
            raise ValueError(
                "Datasets must be cleaned before accessing them."
            )

        return self._paysim_data.copy(), self._ibm_data.copy()

    def combine_data(self) -> pd.DataFrame:
        """Combine the previously cleaned datasets."""

        if self._paysim_data is None or self._ibm_data is None:
            raise ValueError(
                "Datasets must be cleaned before combining."
            )

        return combine_datasets(
            self._paysim_data,
            self._ibm_data
        )

from collections.abc import Iterator
from pathlib import Path

import pandas as pd


PROJECT_DIR = Path(__file__).resolve().parents[1]
PROCESSED_DIR = PROJECT_DIR / "data" / "processed"


def _require_columns(transactions: pd.DataFrame, *columns: str) -> None:
    """Raise an error listing every required column missing from the input."""
    missing_columns = sorted(set(columns).difference(transactions.columns))
    if missing_columns:
        raise ValueError("Missing required columns: " + ", ".join(missing_columns))


def _read_cleaned_transactions(
    path: Path, required_columns: tuple[str, ...]
) -> pd.DataFrame:
    """Read a cleaned CSV and report file or schema errors with its path."""
    try:
        transactions = pd.read_csv(path)
    except FileNotFoundError as error:
        raise FileNotFoundError(
            f"Cleaned dataset not found: {path}. Run python src/main.py first."
        ) from error
    except (
        OSError,
        UnicodeError,
        pd.errors.ParserError,
        pd.errors.EmptyDataError,
    ) as error:
        raise ValueError(f"Could not read cleaned dataset {path}: {error}") from error

    if transactions.empty:
        raise ValueError(f"Cleaned dataset has no transactions: {path}")
    try:
        _require_columns(transactions, *required_columns)
    except ValueError as error:
        raise ValueError(f"Invalid cleaned dataset {path}: {error}") from error
    return transactions


def compute_summary_statistics(
    df: pd.DataFrame,
    amount_column: str,
    currency_column: str | None = None,
    label_column: str = "Is Laundering",
) -> pd.DataFrame:
    """Summarize transaction amounts by label and, when provided, currency."""
    group_columns = [label_column]
    if currency_column is not None:
        group_columns.append(currency_column)

    _require_columns(df, amount_column, *group_columns)
    if not pd.api.types.is_numeric_dtype(df[amount_column]):
        raise ValueError(f"Amount column {amount_column!r} must contain numeric values.")

    grouped = df.groupby(
        group_columns,
        dropna=False,
    )[amount_column]

    summary = grouped.agg(
        total_rows="size",
        count="count",
        mean="mean",
        std="std",
        minimum="min",
        percentile_25=lambda values: values.quantile(0.25),
        median="median",
        percentile_75=lambda values: values.quantile(0.75),
        percentile_90=lambda values: values.quantile(0.90),
        percentile_95=lambda values: values.quantile(0.95),
        percentile_99=lambda values: values.quantile(0.99),
        maximum="max",
        zero_count=lambda values: values.eq(0).sum(),
    ).reset_index()

    summary["missing_count"] = summary["total_rows"] - summary["count"]
    summary["interquartile_range"] = (
        summary["percentile_75"] - summary["percentile_25"]
    )
    return summary


def summarize_category(
    df: pd.DataFrame,
    category_column: str,
    label_column: str,
) -> pd.DataFrame:
    """Count categories and report their share and suspicious-transaction rate."""
    _require_columns(df, category_column, label_column)
    labels = df[label_column]
    if not labels.isin([0, 1]).all():
        raise ValueError(f"Label column {label_column!r} must contain only 0 or 1.")

    categories = df[category_column]
    if categories.hasnans:
        categories = categories.astype(object).fillna("(Missing)")
    counts = pd.crosstab(categories, labels).reindex(columns=[0, 1], fill_value=0)

    summary = counts.rename(
        columns={0: "not_suspicious", 1: "suspicious"}
    ).rename_axis(category_column).reset_index()
    summary["total"] = summary["not_suspicious"] + summary["suspicious"]
    summary["percent"] = 100 * summary["total"] / len(df)
    summary["suspicious_rate"] = (
        100 * summary["suspicious"] / summary["total"]
    )
    return summary


class TransactionSummary:
    """Build amount and category summaries for the cleaned PaySim and IBM data."""

    def __init__(self, processed_dir: Path) -> None:
        """Load and validate both cleaned transaction files from processed_dir."""
        self._paysim = _read_cleaned_transactions(
            processed_dir / "paysim_cleaned.csv", ("amount", "type", "isFraud")
        )
        self._ibm = _read_cleaned_transactions(
            processed_dir / "ibm_cleaned.csv",
            (
                "Amount Received",
                "Receiving Currency",
                "Amount Paid",
                "Payment Currency",
                "Payment Format",
                "Same Bank",
                "Is Laundering",
            ),
        )

    def amount_summaries(self) -> Iterator[tuple[str, pd.DataFrame]]:
        """Yield the three amount tables in display order."""
        yield "PaySim", compute_summary_statistics(
            self._paysim, "amount", label_column="isFraud"
        )
        yield "IBM Amount Received", compute_summary_statistics(
            self._ibm, "Amount Received", "Receiving Currency"
        )
        yield "IBM Amount Paid", compute_summary_statistics(
            self._ibm, "Amount Paid", "Payment Currency"
        )

    def category_summaries(self) -> Iterator[tuple[str, pd.DataFrame]]:
        """Yield each category table with counts and suspicious rates."""
        yield "PaySim transaction type", summarize_category(
            self._paysim, "type", "isFraud"
        )
        for title, column in (
            ("IBM payment format", "Payment Format"),
            ("IBM receiving currency", "Receiving Currency"),
            ("IBM payment currency", "Payment Currency"),
            ("IBM same bank", "Same Bank"),
        ):
            yield title, summarize_category(self._ibm, column, "Is Laundering")


def main() -> None:
    """Print all summaries for the project's cleaned transaction datasets."""
    summary = TransactionSummary(PROCESSED_DIR)
    for title, table in summary.amount_summaries():
        print(f"\nSummary statistics for {title}:")
        print(table.to_string(index=False))

    for title, table in summary.category_summaries():
        print(f"\nCategorical summary for {title}:")
        print(table.to_string(index=False))


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError) as error:
        raise SystemExit(f"Summary statistics failed: {error}") from error

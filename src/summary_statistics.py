from pathlib import Path
import sys

import pandas as pd


PROJECT_DIR = Path(__file__).resolve().parents[1]

if __package__ in (None, ""):
    sys.path.insert(0, str(PROJECT_DIR))

from src.data_processing import clean_ibm


def compute_summary_statistics(
    df: pd.DataFrame,
    amount_column: str,
    currency_column: str,
    label_column: str = "Is Laundering",
) -> pd.DataFrame:
    """Summarize transaction amounts by laundering label and currency."""
    grouped = df.groupby(
        [label_column, currency_column],
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


def main() -> None:
    ibm_file = PROJECT_DIR / "data" / "IBM_small_HI_data" / "HI-Small_Trans.csv"
    ibm = clean_ibm(ibm_file)

    amount_summaries = (
        ("Amount Received", "Receiving Currency"),
        ("Amount Paid", "Payment Currency"),
    )

    for amount_column, currency_column in amount_summaries:
        print(f"\nSummary statistics for {amount_column}:")
        print(
            compute_summary_statistics(
                ibm,
                amount_column,
                currency_column,
            ).to_string(index=False)
        )


if __name__ == "__main__":
    main()

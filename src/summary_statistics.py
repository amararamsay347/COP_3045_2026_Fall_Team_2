from pathlib import Path
import sys

import pandas as pd


PROJECT_DIR = Path(__file__).resolve().parents[1]
PROCESSED_DIR = PROJECT_DIR / "data" / "processed"

if __package__ in (None, ""):
    sys.path.insert(0, str(PROJECT_DIR))


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
    counts = pd.crosstab(
        df[category_column].fillna("(Missing)"),
        df[label_column],
    ).reindex(columns=[0, 1], fill_value=0)

    summary = counts.rename(
        columns={0: "not_suspicious", 1: "suspicious"}
    ).rename_axis(category_column).reset_index()
    summary["total"] = summary["not_suspicious"] + summary["suspicious"]
    summary["percent"] = 100 * summary["total"] / len(df)
    summary["suspicious_rate"] = (
        100 * summary["suspicious"] / summary["total"]
    )
    return summary


def main() -> None:
    paysim_file = PROCESSED_DIR / "paysim_cleaned.csv"
    ibm_file = PROCESSED_DIR / "ibm_cleaned.csv"
    for cleaned_file in (paysim_file, ibm_file):
        if not cleaned_file.is_file():
            raise FileNotFoundError(
                f"Cleaned dataset not found: {cleaned_file}. Run src/main.py first."
            )

    paysim = pd.read_csv(paysim_file)
    ibm = pd.read_csv(ibm_file)

    amount_summaries = (
        ("PaySim", paysim, "amount", None, "isFraud"),
        (
            "IBM Amount Received",
            ibm,
            "Amount Received",
            "Receiving Currency",
            "Is Laundering",
        ),
        (
            "IBM Amount Paid",
            ibm,
            "Amount Paid",
            "Payment Currency",
            "Is Laundering",
        ),
    )

    for title, df, amount_column, currency_column, label_column in amount_summaries:
        print(f"\nSummary statistics for {title}:")
        print(
            compute_summary_statistics(
                df,
                amount_column,
                currency_column,
                label_column,
            ).to_string(index=False)
        )

    category_summaries = (
        ("PaySim transaction type", paysim, "type", "isFraud"),
        ("IBM payment format", ibm, "Payment Format", "Is Laundering"),
        ("IBM receiving currency", ibm, "Receiving Currency", "Is Laundering"),
        ("IBM payment currency", ibm, "Payment Currency", "Is Laundering"),
        ("IBM same bank", ibm, "Same Bank", "Is Laundering"),
    )

    for title, df, category_column, label_column in category_summaries:
        print(f"\nCategorical summary for {title}:")
        print(
            summarize_category(df, category_column, label_column).to_string(
                index=False
            )
        )


if __name__ == "__main__":
    main()

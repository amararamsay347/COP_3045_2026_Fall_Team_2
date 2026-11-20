"""Reusable exploratory analysis calculations for transaction reports."""

from dataclasses import dataclass
import pandas as pd


@dataclass(frozen=True)
class ReportMetrics:
    """Immutable collection of report summaries."""

    source_summary: pd.DataFrame
    category_summary: pd.DataFrame
    amount_summary: pd.DataFrame
    amount_status_summary: pd.DataFrame


def summarize_sources(frame: pd.DataFrame) -> pd.DataFrame:
    """Calculate transaction counts and suspicious rates by source."""
    summary = (
        frame.groupby("dataset_source", observed=True)["is_suspicious"]
        .agg(["count", "sum", "mean"])
        .reset_index()
        .rename(columns={"count": "transaction_count", "sum": "suspicious_count", "mean": "suspicious_rate"})
    )
    summary["suspicious_rate"] *= 100
    return summary


def summarize_categories(frame: pd.DataFrame) -> pd.DataFrame:
    """Calculate suspicious rates for each source/category pair."""
    summary = (
        frame.groupby(["dataset_source", "transaction_category"], observed=True)["is_suspicious"]
        .agg(["count", "sum", "mean"])
        .reset_index()
        .rename(columns={"count": "transaction_count", "sum": "suspicious_count", "mean": "suspicious_rate"})
    )
    summary["suspicious_rate"] *= 100
    summary["display_category"] = (
        summary["dataset_source"].astype(str)
        + " - "
        + summary["transaction_category"].astype(str)
    )
    return summary.sort_values("suspicious_rate", ascending=False)


def summarize_amounts(frame: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Summarize native-currency amounts and suspicious status amounts."""
    currency_counts = (
        frame.groupby(["dataset_source", "currency"], observed=True)
        .size()
        .reset_index(name="transaction_count")
        .sort_values(["dataset_source", "transaction_count"], ascending=[True, False])
    )
    main_currencies = currency_counts.groupby("dataset_source", observed=True).first().reset_index()

    amount_rows: list[dict[str, object]] = []
    status_rows: list[dict[str, object]] = []
    for row in main_currencies.itertuples(index=False):
        source_data = frame[(frame["dataset_source"] == row.dataset_source) & (frame["currency"] == row.currency)]
        amounts = source_data["transaction_amount"].dropna()
        amount_rows.append({
            "dataset_source": str(row.dataset_source), "currency": str(row.currency),
            "count": amounts.count(), "mean": amounts.mean(), "std": amounts.std(),
            "percentile_25": amounts.quantile(0.25), "median": amounts.median(),
            "percentile_75": amounts.quantile(0.75), "minimum": amounts.min(), "maximum": amounts.max(),
        })
        for status, status_name in ((0, "Not Suspicious"), (1, "Suspicious")):
            status_amounts = source_data.loc[source_data["is_suspicious"] == status, "transaction_amount"].dropna()
            status_rows.append({
                "dataset_source": str(row.dataset_source), "currency": str(row.currency),
                "status": status_name, "count": status_amounts.count(),
                "mean_amount": status_amounts.mean(), "median_amount": status_amounts.median(),
            })

    amount_summary = pd.DataFrame(amount_rows)
    status_summary = pd.DataFrame(status_rows)
    if not status_summary.empty:
        status_summary["display_source"] = status_summary["dataset_source"] + " (" + status_summary["currency"] + ")"
    return amount_summary, status_summary


def build_metrics(frame: pd.DataFrame) -> ReportMetrics:
    """Build all DataFrame metrics used by charts and PDF tables."""
    amount_summary, amount_status_summary = summarize_amounts(frame)
    return ReportMetrics(
        source_summary=summarize_sources(frame),
        category_summary=summarize_categories(frame),
        amount_summary=amount_summary,
        amount_status_summary=amount_status_summary,
    )

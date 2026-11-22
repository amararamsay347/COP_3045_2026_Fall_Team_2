"""Statistics used by the PDF report, independent of rendering."""

import pandas as pd


def _label_summary(df: pd.DataFrame, groups: list[str]) -> pd.DataFrame:
    """Calculate transaction counts, positive counts, and rates by group."""
    summary = (
        df.groupby(groups, observed=True)["is_suspicious"]
        .agg(transaction_count="size", suspicious_count="sum", suspicious_rate="mean")
        .reset_index()
    )
    summary["suspicious_rate"] *= 100
    return summary


def summarize_sources(df: pd.DataFrame) -> pd.DataFrame:
    """Count each source's positive labels using its own denominator."""
    return _label_summary(df, ["dataset_source", "label_type"])


def summarize_categories(df: pd.DataFrame) -> pd.DataFrame:
    """Rank categories by positive-label rate within each source."""
    summary = _label_summary(df, ["dataset_source", "transaction_category"])
    summary["display_category"] = (
        summary["dataset_source"].astype(str)
        + " - "
        + summary["transaction_category"].astype(str)
    )
    return summary.sort_values(
        ["dataset_source", "suspicious_rate", "suspicious_count", "transaction_category"],
        ascending=[True, False, False, True],
    )


def highlight_categories(category_summary: pd.DataFrame) -> pd.DataFrame:
    """Select the three highest rates and the largest flagged count per source."""
    groups = category_summary.groupby("dataset_source", observed=True)
    counts = category_summary.sort_values("suspicious_count", ascending=False, kind="stable")
    leaders = counts.groupby("dataset_source", observed=True).head(1)
    return (
        pd.concat([groups.head(3), leaders])
        .drop_duplicates(["dataset_source", "transaction_category"])
        .sort_values(["dataset_source", "suspicious_rate"], ascending=[True, False])
    )


def build_findings(
    num_rows: int,
    source_summary: pd.DataFrame,
    category_summary: pd.DataFrame,
    amount_status_summary: pd.DataFrame,
) -> list[str]:
    """Describe label rates, category counts, and amount medians by source."""
    findings = [f"The combined dataset contains {num_rows:,} transactions."]
    for source in source_summary.itertuples(index=False):
        findings.append(
            f"{source.dataset_source} flagged {source.suspicious_count:,} of "
            f"{source.transaction_count:,} transactions for {source.label_type} "
            f"({source.suspicious_rate:.4f}%)."
        )
        categories = category_summary.loc[
            (category_summary["dataset_source"] == source.dataset_source)
            & category_summary["suspicious_count"].gt(0)
        ]
        if categories.empty:
            continue
        rate_leader = categories.iloc[0]
        count_leader = categories.loc[categories["suspicious_count"].idxmax()]
        findings.append(
            f"In {source.dataset_source}, {rate_leader.transaction_category} had the "
            f"highest {source.label_type} label rate ({rate_leader.suspicious_rate:.4f}%). "
            f"{count_leader.transaction_category} had the most positive labels "
            f"({count_leader.suspicious_count:,})."
        )

    for source, group in amount_status_summary.groupby("display_source"):
        medians = group.set_index("status")["median_amount"]
        flagged = medians["Suspicious"]
        unflagged = medians["Not Suspicious"]
        if pd.notna(flagged) and unflagged > 0:
            findings.append(
                f"In {source}, the flagged median ({flagged:,.2f}) was "
                f"{flagged / unflagged:.1f}x the unflagged median ({unflagged:,.2f})."
            )

    findings.append(
        "These synthetic datasets use different definitions of a positive label. "
        "Interpret each rate within its source and each amount within its currency."
    )
    return findings


def summarize_amounts(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Summarize amounts by source in its most common currency."""
    currency_counts = (
        df.groupby(["dataset_source", "currency"], observed=True)
        .size()
        .reset_index(name="transaction_count")
        .sort_values(["dataset_source", "transaction_count"], ascending=[True, False])
    )
    main_currencies = currency_counts.groupby("dataset_source", observed=True).head(1)
    amount_rows = []
    status_rows = []
    for row in main_currencies.itertuples(index=False):
        source_amounts = df.loc[
            df["dataset_source"].eq(row.dataset_source) & df["currency"].eq(row.currency),
            ["transaction_amount", "is_suspicious"],
        ]
        amounts = source_amounts["transaction_amount"].dropna()
        amount_rows.append(
            {
                "dataset_source": row.dataset_source,
                "currency": row.currency,
                "count": amounts.count(),
                "mean": amounts.mean(),
                "std": amounts.std(),
                "percentile_25": amounts.quantile(0.25),
                "median": amounts.median(),
                "percentile_75": amounts.quantile(0.75),
                "minimum": amounts.min(),
                "maximum": amounts.max(),
            }
        )
        for label, status in ((0, "Not Suspicious"), (1, "Suspicious")):
            status_amounts = source_amounts.loc[
                source_amounts["is_suspicious"].eq(label), "transaction_amount"
            ]
            status_rows.append(
                {
                    "dataset_source": row.dataset_source,
                    "currency": row.currency,
                    "status": status,
                    "count": status_amounts.count(),
                    "mean_amount": status_amounts.mean(),
                    "median_amount": status_amounts.median(),
                    "display_source": f"{row.dataset_source} ({row.currency})",
                }
            )
    return pd.DataFrame(amount_rows), pd.DataFrame(status_rows)

"""Graphical EDA of the combined cleaned PAYSim and IBM transactions.

Run src/main.py first to create 03-Data cleaning/clean_data.csv.
Charts are saved to 04-EDA/output/ when this script is run manually.
"""

from pathlib import Path
import re

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import StrMethodFormatter
import pandas as pd
import seaborn as sns


PROJECT_DIR = Path(__file__).resolve().parents[1]
CLEAN_DATA_FILE = PROJECT_DIR / "03-Data cleaning" / "clean_data.csv"
OUTPUT_DIR = Path(__file__).resolve().parent / "output"
IBM_METADATA_DIR = PROJECT_DIR / "data" / "ibm" / "IBM_small_HI_data"
IBM_ACCOUNTS_FILE = IBM_METADATA_DIR / "HI-Small_accounts.csv"
IBM_PATTERNS_FILE = IBM_METADATA_DIR / "HI-Small_Patterns.csv"

# Read only the fields used below to reduce memory use for the large CSV.
EDA_COLUMNS = {
    "dataset_source",
    "transaction_amount",
    "currency",
    "transaction_category",
    "is_suspicious",
    "label_type",
    "step",
    "Timestamp",
    "origin_balance_change",
}


def load_data() -> pd.DataFrame:
    """Read the assignment's cleaned CSV into a DataFrame named df."""
    if not CLEAN_DATA_FILE.is_file():
        raise FileNotFoundError(
            f"Cleaned dataset not found: {CLEAN_DATA_FILE}. "
            "Run src/main.py from the project folder first."
        )

    df = pd.read_csv(
        CLEAN_DATA_FILE,
        usecols=lambda column: column in EDA_COLUMNS,
        dtype={
            "dataset_source": "category",
            "currency": "category",
            "transaction_category": "category",
            "label_type": "category",
        },
        low_memory=False,
    )
    missing_columns = EDA_COLUMNS.difference(df.columns)
    if missing_columns:
        raise ValueError(
            "Cleaned dataset is missing EDA columns: "
            + ", ".join(sorted(missing_columns))
            + ". Recreate it with src/main.py."
        )
    if df.empty:
        raise ValueError("The cleaned dataset contains no transaction rows.")

    numeric_columns = (
        "transaction_amount", "is_suspicious", "step", "origin_balance_change"
    )
    for column in numeric_columns:
        df[column] = pd.to_numeric(df[column], errors="coerce").replace(
            [float("inf"), float("-inf")], float("nan")
        )
    sources = set(df["dataset_source"].dropna().unique())
    if not {"PAYSim", "IBM"}.issubset(sources):
        raise ValueError(
            "Expected combined PAYSim and IBM transactions. "
            "Recreate the cleaned CSV with src/main.py."
        )
    return df


def _entity_type(entity_name: object) -> str:
    """Strip the numbered entity suffix without changing the entity type."""
    if pd.isna(entity_name):
        return "Unknown"
    value = str(entity_name).strip()
    return re.split(r"\s*#\s*\d+$", value, maxsplit=1)[0].strip() or "Unknown"


def load_ibm_accounts() -> pd.DataFrame | None:
    """Load the optional account registry, preserving identifier strings."""
    if not IBM_ACCOUNTS_FILE.is_file():
        print(f"Skipping optional account chart: file not found: {IBM_ACCOUNTS_FILE}")
        return None
    try:
        accounts = pd.read_csv(
            IBM_ACCOUNTS_FILE,
            usecols=["Bank ID", "Account Number", "Entity ID", "Entity Name"],
            dtype="string",
        )
    except (OSError, ValueError) as error:
        print(f"Skipping optional account chart: {error}")
        return None
    accounts["entity_type"] = accounts["Entity Name"].map(_entity_type)
    return accounts


def load_ibm_patterns() -> pd.DataFrame | None:
    """Load optional pattern transaction rows and group configuration variants."""
    if not IBM_PATTERNS_FILE.is_file():
        print(f"Skipping optional pattern chart: file not found: {IBM_PATTERNS_FILE}")
        return None
    try:
        patterns = pd.read_csv(
            IBM_PATTERNS_FILE, usecols=["pattern"], dtype="string"
        )
    except (OSError, ValueError) as error:
        print(f"Skipping optional pattern chart: {error}")
        return None
    patterns["pattern_label"] = (
        patterns["pattern"]
        .str.replace("BEGIN LAUNDERING ATTEMPT - ", "", regex=False)
        .str.split(":", n=1)
        .str[0]
        .str.strip()
        .fillna("Unknown")
        .replace("", "Unknown")
    )
    return patterns


def create_summary_tables(
    df: pd.DataFrame,
    accounts_df: pd.DataFrame | None = None,
    patterns_df: pd.DataFrame | None = None,
) -> None:
    """Print concise summaries without averaging amounts across currencies."""
    print(
        f"Cleaned EDA data: {len(df):,} transaction rows; "
        f"{len(df.columns)} selected columns"
    )
    print("\nTransaction labels by source (fraud and laundering are separate labels):")
    print(
        df.groupby(["dataset_source", "label_type"], observed=True)
        .agg(
            transaction_count=("dataset_source", "size"),
            flagged_count=("is_suspicious", "sum"),
        )
        .to_string()
    )
    print("\nMissing values in EDA fields (some fields are source-specific):")
    print(df.isna().sum().to_string())
    print("\nIBM amounts by native currency:")
    print(
        df.loc[df["dataset_source"].eq("IBM")]
        .groupby("currency", observed=True)["transaction_amount"]
        .agg(["count", "median", "mean", "max"])
        .sort_values("count", ascending=False)
        .round(2)
        .to_string()
    )
    if patterns_df is not None:
        print("\nTransaction records in the pattern CSV by pattern family:")
        print(patterns_df["pattern_label"].value_counts().to_string())
    if accounts_df is not None:
        print("\nIBM account registry:")
        print(
            pd.Series(
                {
                    "account_records": len(accounts_df),
                    "unique_banks": accounts_df["Bank ID"].nunique(),
                    "unique_entity_ids": accounts_df["Entity ID"].nunique(),
                }
            ).to_string()
        )
        print("\nAccount records by entity type:")
        print(accounts_df["entity_type"].value_counts().to_string())


def _save_figure(fig, filename: str, note: str | None = None) -> None:
    """Save and close a figure, leaving room for an explanatory note."""
    if note:
        fig.text(0.5, 0.015, note, ha="center", fontsize=9)
        fig.tight_layout(rect=(0, 0.07, 1, 1))
    else:
        fig.tight_layout()
    fig.savefig(OUTPUT_DIR / filename, dpi=300, bbox_inches="tight")
    plt.close(fig)
    print(f"Saved chart: {OUTPUT_DIR / filename}")


def _plot_counts(
    counts: pd.Series, ax, title: str, ylabel: str, color: str
) -> None:
    """Draw category counts with labels that also expose very small categories."""
    counts = counts.sort_values(ascending=False)
    if counts.empty:
        ax.set(title=title, xlabel="Number of records", ylabel=ylabel)
        ax.text(
            0.5, 0.5, "No records available", ha="center", transform=ax.transAxes
        )
        return
    sns.barplot(
        x=counts.to_numpy(), y=counts.index.astype(str), color=color, ax=ax
    )
    ax.bar_label(
        ax.containers[0],
        labels=[f"{count:,}" for count in counts],
        padding=3,
        fontsize=9,
    )
    ax.set(title=title, xlabel="Number of records", ylabel=ylabel)
    ax.set_xlim(0, counts.max() * 1.25)
    ax.xaxis.set_major_formatter(StrMethodFormatter("{x:,.0f}"))
    ax.grid(axis="y", visible=False)
    ax.grid(axis="x", linestyle="--", alpha=0.5)


def _plot_currency_distribution(df: pd.DataFrame) -> None:
    """Explore IBM amount distributions within each native currency."""
    amounts = df.loc[
        df["dataset_source"].eq("IBM")
        & df["transaction_amount"].gt(0)
        & df["currency"].notna(),
        ["currency", "transaction_amount"],
    ]
    if amounts.empty:
        raise ValueError(
            "No positive IBM amounts with a currency are available for the box plot."
        )
    top_currencies = amounts["currency"].value_counts().head(6).index
    amounts = amounts.loc[amounts["currency"].isin(top_currencies)]
    fig, ax = plt.subplots(figsize=(11, 6))
    sns.boxplot(
        data=amounts,
        x="currency",
        y="transaction_amount",
        order=top_currencies,
        color="#76B7B2",
        showfliers=False,
        ax=ax,
    )
    ax.set(
        title="IBM Received Amount Distribution by Currency",
        xlabel="Receiving currency",
        ylabel="Amount received (native units; log scale)",
        yscale="log",
    )
    ax.tick_params(axis="x", rotation=25)
    _save_figure(
        fig,
        "received_amount_distribution_by_currency.png",
        "Six most common currencies. Positive amounts only; "
        "outlier markers hidden. Currencies are not converted.",
    )


def _plot_transaction_categories(df: pd.DataFrame) -> None:
    """Compare transaction categories separately for the two datasets."""
    fig, axes = plt.subplots(1, 2, figsize=(15, 6))
    for ax, source, color in zip(
        axes, ("PAYSim", "IBM"), ("#2E9BDE", "#76B79F")
    ):
        counts = df.loc[
            df["dataset_source"].eq(source), "transaction_category"
        ].value_counts(dropna=False)
        counts = counts.loc[counts.gt(0)]
        _plot_counts(
            counts, ax, f"{source} Transaction Counts by Category", "Category", color
        )
        ax.set_xlabel("Number of transactions")
    _save_figure(fig, "transaction_counts_by_category.png")


def _plot_amount_balance_relationship(df: pd.DataFrame) -> None:
    """Explore a numerical relationship in PAYSim with a reproducible sample."""
    paysim = df.loc[
        df["dataset_source"].eq("PAYSim")
        & df["transaction_amount"].gt(0)
        & df["origin_balance_change"].notna(),
        ["transaction_amount", "origin_balance_change", "is_suspicious"],
    ]
    if paysim.empty:
        raise ValueError(
            "No valid PAYSim amounts and origin balance changes are available "
            "for the scatter plot."
        )
    sample = paysim.sample(n=min(5_000, len(paysim)), random_state=42).copy()
    sample["fraud_status"] = (
        sample["is_suspicious"]
        .map({0: "Not fraud", 1: "Fraud"})
        .fillna("Unknown")
    )
    hue_order = [
        label
        for label in ("Not fraud", "Fraud", "Unknown")
        if label in sample["fraud_status"].values
    ]
    fig, ax = plt.subplots(figsize=(11, 6))
    sns.scatterplot(
        data=sample,
        x="transaction_amount",
        y="origin_balance_change",
        hue="fraud_status",
        hue_order=hue_order,
        palette={
            "Not fraud": "#2E86DE", "Fraud": "#D64541", "Unknown": "#808080"
        },
        alpha=0.5,
        s=18,
        linewidth=0,
        ax=ax,
    )
    ax.set(
        title="PAYSim Transaction Amount vs. Origin Balance Change",
        xlabel="Transaction amount (PAYSim units; log scale)",
        ylabel="Origin balance change (PAYSim units; symmetric log scale)",
        xscale="log",
    )
    ax.set_yscale("symlog", linthresh=1)
    ax.legend(title="Fraud status")
    _save_figure(
        fig,
        "transaction_amount_vs_origin_balance_change.png",
        f"Random sample of {len(sample):,} rows with positive amounts. "
        "Negative balance changes indicate a decrease.",
    )


def _plot_daily_volume(df: pd.DataFrame) -> None:
    """Use simulation days for PAYSim and recorded calendar dates for IBM."""
    steps = df.loc[df["dataset_source"].eq("PAYSim"), "step"].dropna()
    steps = steps.loc[steps.ge(1)]
    paysim_days = ((steps - 1) // 24 + 1).astype("int64")
    paysim_counts = paysim_days.value_counts().sort_index()
    timestamps = pd.to_datetime(
        df.loc[df["dataset_source"].eq("IBM"), "Timestamp"], errors="coerce"
    )
    ibm_counts = timestamps.dropna().dt.floor("D").value_counts().sort_index()
    if paysim_counts.empty or ibm_counts.empty:
        raise ValueError(
            "Valid PAYSim simulation steps and IBM timestamps are required "
            "for daily volume charts."
        )
    paysim_counts = paysim_counts.reindex(
        range(paysim_counts.index.min(), paysim_counts.index.max() + 1),
        fill_value=0,
    )
    ibm_counts = ibm_counts.reindex(
        pd.date_range(ibm_counts.index.min(), ibm_counts.index.max(), freq="D"),
        fill_value=0,
    )
    fig, axes = plt.subplots(1, 2, figsize=(15, 5))
    for ax, counts, source, xlabel in (
        (axes[0], paysim_counts, "PAYSim", "Simulation day"),
        (axes[1], ibm_counts, "IBM", "Recorded date"),
    ):
        sns.lineplot(
            x=counts.index, y=counts.to_numpy(),
            marker="o", color="#2E86DE", ax=ax,
        )
        ax.set(
            title=f"{source} Daily Transaction Volume",
            xlabel=xlabel,
            ylabel="Number of transactions",
        )
        ax.yaxis.set_major_formatter(StrMethodFormatter("{x:,.0f}"))
        ax.set_ylim(bottom=0)
        ax.grid(linestyle="--", alpha=0.5)
    axes[1].tick_params(axis="x", rotation=35)
    _save_figure(
        fig,
        "daily_transaction_volume.png",
        "PAYSim day 1 contains simulation steps 1-24; "
        "IBM uses its original timestamps.",
    )


def create_visualizations(
    df: pd.DataFrame,
    accounts_df: pd.DataFrame | None = None,
    patterns_df: pd.DataFrame | None = None,
) -> None:
    """Create four cleaned-data charts and optional metadata supplements."""
    sns.set_theme(style="whitegrid", context="notebook", font_scale=1.1)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Distribution, category comparison, numerical relationship, and time trend.
    _plot_currency_distribution(df)
    _plot_transaction_categories(df)
    _plot_amount_balance_relationship(df)
    _plot_daily_volume(df)

    if patterns_df is not None and not patterns_df.empty:
        fig, ax = plt.subplots(figsize=(11, 6))
        _plot_counts(
            patterns_df["pattern_label"].value_counts(),
            ax,
            "IBM Transaction Records by Laundering Pattern",
            "Pattern family",
            "#6B4C9A",
        )
        ax.set_xlabel("Number of transaction records")
        _save_figure(
            fig, "transaction_counts_by_pattern.png",
            "Counts describe transaction rows in HI-Small_Patterns.csv.",
        )

    if accounts_df is not None and not accounts_df.empty:
        fig, ax = plt.subplots(figsize=(11, 6))
        _plot_counts(
            accounts_df["entity_type"].value_counts(),
            ax,
            "IBM Account Records by Entity Type",
            "Entity type",
            "#7B3F8C",
        )
        ax.set_xlabel("Number of account records")
        _save_figure(fig, "account_records_by_entity_type.png")


def main() -> None:
    df = load_data()
    accounts_df = load_ibm_accounts()
    patterns_df = load_ibm_patterns()
    create_summary_tables(df, accounts_df, patterns_df)
    create_visualizations(df, accounts_df, patterns_df)


if __name__ == "__main__":
    main()

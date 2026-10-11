from collections import defaultdict
from pathlib import Path

import numpy as np
import pandas as pd


PROJECT_DIR = Path(__file__).resolve().parents[1]
COMBINED_FILE = PROJECT_DIR / "data" / "processed" / "combined_transactions.csv"
CHUNK_SIZE = 250_000
REQUIRED_COLUMNS = [
    "transaction_amount",
    "currency",
    "transaction_category",
    "dataset_source",
    "label_type",
    "is_suspicious",
]


def _amount_summary(values: np.ndarray, total_rows: int) -> dict[str, float | int]:
    amounts = pd.Series(values)
    return {
        "total_rows": total_rows,
        "count": int(amounts.count()),
        "missing_count": total_rows - int(amounts.count()),
        "mean": amounts.mean(),
        "std": amounts.std(),
        "minimum": amounts.min(),
        "percentile_25": amounts.quantile(0.25),
        "median": amounts.median(),
        "percentile_75": amounts.quantile(0.75),
        "percentile_90": amounts.quantile(0.90),
        "percentile_95": amounts.quantile(0.95),
        "percentile_99": amounts.quantile(0.99),
        "maximum": amounts.max(),
        "zero_count": int(amounts.eq(0).sum()),
        "interquartile_range": amounts.quantile(0.75) - amounts.quantile(0.25),
    }


def _print_categorical_summary(
    category: str,
    counts: dict[tuple[str, str, str], list[int]],
    source_totals: dict[tuple[str, str], int],
) -> None:
    rows = []
    for (source, label_type, value), outcome_counts in sorted(counts.items()):
        not_suspicious, suspicious = outcome_counts
        total = not_suspicious + suspicious
        rows.append(
            {
                "dataset_source": source,
                "label_type": label_type,
                category: value,
                "not_suspicious": not_suspicious,
                "suspicious": suspicious,
                "total": total,
                "percent": 100 * total / source_totals[(source, label_type)],
                "suspicious_rate": 100 * suspicious / total if total else 0,
            }
        )

    print(f"\nCategorical summary for {category}:")
    print(pd.DataFrame(rows).to_string(index=False))


def main() -> None:
    if not COMBINED_FILE.is_file():
        raise FileNotFoundError(
            f"Combined dataset not found: {COMBINED_FILE}. Run src/main.py first."
        )

    header = pd.read_csv(COMBINED_FILE, nrows=0)
    missing_columns = sorted(set(REQUIRED_COLUMNS) - set(header.columns))
    if missing_columns:
        raise ValueError(
            f"Combined dataset is missing required columns: {missing_columns}"
        )

    amount_values: dict[tuple[str, str, str, int], list[np.ndarray]] = defaultdict(list)
    amount_totals: dict[tuple[str, str, str, int], int] = defaultdict(int)
    source_totals: dict[tuple[str, str], int] = defaultdict(int)
    category_counts: dict[
        str, dict[tuple[str, str, str], list[int]]
    ] = {
        "transaction_category": defaultdict(lambda: [0, 0]),
        "currency": defaultdict(lambda: [0, 0]),
    }

    for chunk in pd.read_csv(
        COMBINED_FILE,
        usecols=REQUIRED_COLUMNS,
        chunksize=CHUNK_SIZE,
        dtype={
            "transaction_amount": "float64",
            "currency": "string",
            "transaction_category": "string",
            "dataset_source": "string",
            "label_type": "string",
            "is_suspicious": "int8",
        },
    ):
        for column in ("currency", "transaction_category", "dataset_source", "label_type"):
            chunk[column] = chunk[column].fillna("(Missing)").astype(str)

        chunk["transaction_amount"] = pd.to_numeric(
            chunk["transaction_amount"], errors="coerce"
        )
        chunk["is_suspicious"] = pd.to_numeric(
            chunk["is_suspicious"], errors="raise"
        ).astype(int)
        if not chunk["is_suspicious"].isin([0, 1]).all():
            raise ValueError("is_suspicious must contain only 0 and 1.")

        source_groups = chunk.groupby(
            ["dataset_source", "label_type"], sort=False
        ).size()
        for key, count in source_groups.items():
            source_totals[key] += int(count)

        amount_keys = [
            "dataset_source",
            "label_type",
            "currency",
            "is_suspicious",
        ]
        for key, group in chunk.groupby(amount_keys, sort=False, dropna=False):
            amount_totals[key] += len(group)
            values = group["transaction_amount"].dropna().to_numpy()
            if values.size:
                amount_values[key].append(values)

        for category in category_counts:
            grouped = chunk.groupby(
                ["dataset_source", "label_type", category, "is_suspicious"],
                sort=False,
                dropna=False,
            ).size()
            for (source, label_type, value, outcome), count in grouped.items():
                category_counts[category][
                    (source, label_type, value)
                ][outcome] += int(count)

    amount_rows = []
    for key, total_rows in sorted(amount_totals.items()):
        values = np.concatenate(amount_values[key]) if amount_values[key] else np.array([])
        source, label_type, currency, outcome = key
        amount_rows.append(
            {
                "dataset_source": source,
                "label_type": label_type,
                "currency": currency,
                "is_suspicious": outcome,
                **_amount_summary(values, total_rows),
            }
        )

    print("\nNumerical summary for transaction_amount:")
    print(pd.DataFrame(amount_rows).to_string(index=False))

    for category, counts in category_counts.items():
        _print_categorical_summary(category, counts, source_totals)


if __name__ == "__main__":
    main()

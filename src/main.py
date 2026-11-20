"""Prepare cleaned PaySim and IBM data for the analysis workflow."""

from pathlib import Path
import sys

PROJECT_DIR = Path(__file__).resolve().parents[1]
if __package__ in (None, ""):
    sys.path.insert(0, str(PROJECT_DIR))

from src.data_processing import (
    clean_ibm,
    clean_paysim,
    combine_datasets,
    inspect_paysim,
)

PAYSIM_FILE = PROJECT_DIR / "data" / "paysim_data.csv"
IBM_FILE = PROJECT_DIR / "data" / "IBM_small_Hi_data" / "HI-Small_Trans.csv"
PROCESSED_DIR = PROJECT_DIR / "data" / "processed"
CLEAN_DATA_FILE = PROJECT_DIR / "03-Data cleaning" / "clean_data.csv"


def main() -> None:
    """Clean both source datasets and save files consumed by later stages."""
    inspect_paysim(PAYSIM_FILE)
    print("\n" + "=" * 50 + "\n")

    paysim = clean_paysim(PAYSIM_FILE)
    ibm = clean_ibm(IBM_FILE)

    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    paysim_output = PROCESSED_DIR / "paysim_cleaned.csv"
    ibm_output = PROCESSED_DIR / "ibm_cleaned.csv"
    combined_output = PROCESSED_DIR / "combined_transactions.csv"
    paysim.to_csv(paysim_output, index=False)
    ibm.to_csv(ibm_output, index=False)

    combined = combine_datasets(paysim, ibm)
    combined.to_csv(combined_output, index=False)
    CLEAN_DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    combined.to_csv(CLEAN_DATA_FILE, index=False, chunksize=100_000)

    print("\nPaySim cleaned data head:")
    print(paysim.head())
    print("\nPaySim cleaned data shape:")
    print(paysim.shape)
    print("\nIBM cleaned data head:")
    print(ibm.head())
    print("\nIBM cleaned data shape:")
    print(ibm.shape)

    print("\nPaySim fraud labels:")
    print(paysim["isFraud"].value_counts())
    print("\nIBM laundering labels:")
    print(ibm["Is Laundering"].value_counts())
    print("\nPaySim transaction types:")
    print(paysim["type"].value_counts())
    print("\nIBM payment formats:")
    print(ibm["Payment Format"].value_counts())
    print("\nPaySim hours:")
    print(paysim["hour"].describe())
    print("\nIBM hours:")
    print(ibm["hour"].describe())

    print(f"\nCleaned PaySim dataset saved to: {paysim_output}")
    print(f"Cleaned IBM dataset saved to: {ibm_output}")
    print(f"Combined dataset saved to: {combined_output}")
    print(f"EDA dataset saved to: {CLEAN_DATA_FILE}")


if __name__ == "__main__":
    main()

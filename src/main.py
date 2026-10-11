from pathlib import Path
import sys

# Resolve the project root so the script can find data files and package imports reliably.
PROJECT_DIR = Path(__file__).resolve().parents[1]

# Allow the project package to be imported when this script is run directly.
if __package__ in (None, ""):
    sys.path.insert(0, str(PROJECT_DIR))

# Import the dataset inspection and cleaning functions used by the main workflow.
from src.data_processing import (
    clean_ibm,
    clean_paysim,
    combine_datasets,
    inspect_ibm,
    inspect_paysim,
)


# Store the dataset paths in one place so they are easy to update later.
PAYSIM_FILE = PROJECT_DIR / "data" / "ibm" / "paysim_data.csv"
IBM_FILE = PROJECT_DIR / "data" / "IBM_small_HI_data" / "HI-Small_Trans.csv"
PROCESSED_DIR = PROJECT_DIR / "data" / "processed"


def main():
    # Inspect the raw datasets before cleaning.
    inspect_paysim(PAYSIM_FILE)
    inspect_ibm(IBM_FILE.parent)

    print("\n" + "=" * 50 + "\n")

    # Clean the PaySim dataset by keeping the fields needed for analysis
    # and creating the derived balance and time variables.
    paysim = clean_paysim(PAYSIM_FILE)

    # Clean the IBM transaction dataset by selecting the important fields,
    # converting timestamps, and creating derived variables.
    ibm = clean_ibm(IBM_FILE)

    # Save cleaned datasets so the summary-statistics script can analyze these outputs.
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    paysim_output = PROCESSED_DIR / "paysim_cleaned.csv"
    ibm_output = PROCESSED_DIR / "ibm_cleaned.csv"
    paysim.to_csv(paysim_output, index=False)
    ibm.to_csv(ibm_output, index=False)

    # Show the cleaned PaySim preview and overall shape.
    print("\nPaySim cleaned data head:")
    print(paysim.head())

    print("\nPaySim cleaned data shape:")
    print(paysim.shape)

    # Show the cleaned IBM preview and overall shape.
    print("\nIBM cleaned data head:")
    print(ibm.head())

    print("\nIBM cleaned data shape:")
    print(ibm.shape)

    # Print the distribution of fraudulent and legitimate PaySim transactions.
    print("\nPaySim fraud labels:")
    print(paysim["isFraud"].value_counts())

    # Print the distribution of laundering and non-laundering IBM transactions.
    print("\nIBM laundering labels:")
    print(ibm["Is Laundering"].value_counts())

    # Summarize the different transaction categories in PaySim.
    print("\nPaySim transaction types:")
    print(paysim["type"].value_counts())

    # Summarize the different payment formats in IBM.
    print("\nIBM payment formats:")
    print(ibm["Payment Format"].value_counts())

    # Summarize the derived transaction-hour variable for PaySim.
    print("\nPaySim hours:")
    print(paysim["hour"].describe())

    # Summarize the derived transaction-hour variable for IBM.
    print("\nIBM hours:")
    print(ibm["hour"].describe())

    # Combine both sources using the shared analytical fields.
    combined = combine_datasets(paysim, ibm)
    combined_path = PROCESSED_DIR / "combined_transactions.csv"
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    combined.to_csv(combined_path, index=False)

    print("\nCombined analytical data shape:")
    print(combined.shape)
    print(f"Combined dataset saved to: {combined_path}")

    print(f"\nCleaned PaySim dataset saved to: {paysim_output}")
    print(f"Cleaned IBM dataset saved to: {ibm_output}")


# Run the main workflow only when this file is executed directly.
if __name__ == "__main__":
    main()
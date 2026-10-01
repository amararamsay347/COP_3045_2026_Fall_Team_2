from pathlib import Path
import sys

# Resolve the project root so the script can find data files and package imports reliably.
PROJECT_DIR = Path(__file__).resolve().parents[1]

# Allow the project package to be imported when this script is run directly.
if __package__ in (None, ""):
    sys.path.insert(0, str(PROJECT_DIR))

# Import the dataset inspection and cleaning functions used by the main workflow.
from src.data_processing import clean_ibm, clean_paysim, inspect_paysim, inspect_ibm


def main():
    # Inspect the raw PAYSim CSV to review its size, columns, and missing-data issues.
    inspect_paysim(PROJECT_DIR / "paysim_data.csv")

    print("\n" + "=" * 50 + "\n")

    # Inspect every IBM CSV in the folder to summarize schema and data quality before cleaning.
    inspect_ibm(PROJECT_DIR / "IBM_small_HI_data")

    # Clean the PAYSim dataset by keeping only essential fraud-analysis columns and derived fields.
    paysim = clean_paysim(PROJECT_DIR / "paysim_data.csv")

    # Clean the IBM dataset by selecting key fields, standardizing labels, and adding useful timestamps.
    ibm = clean_ibm(PROJECT_DIR / "IBM_small_HI_data" / "HI-Small_Trans.csv")

    # Show the cleaned PAYSim preview and overall shape for comparison with the raw data.
    print("\nPaysim cleaned data head: ")
    print(paysim.head())

    print("\nPaysim cleaned data shape: ")
    print(paysim.shape)

    # Show the cleaned IBM preview and overall shape for the same validation step.
    print("\nIBM cleaned data head: ")
    print(ibm.head())

    print("\nIBM cleaned data shape: ")
    print(ibm.shape)

    # Print the distribution of fraudulent and legitimate PAYSim transactions.
    print("\nPAYSim fraud labels:")
    print(paysim["isFraud"].value_counts())

    # Print the distribution of laundering and non-laundering IBM records.
    print("\nIBM laundering labels:")
    print(ibm["Is Laundering"].value_counts())

    # Summarize the different transaction categories in PAYSim.
    print("\nPAYSim transaction types:")
    print(paysim["type"].value_counts())

    # Summarize payment-format categories in the IBM dataset.
    print("\nIBM payment formats:")
    print(ibm["Payment Format"].value_counts())

    print("\nPAYSim hours:")
    print(paysim["hour"].describe())

    print("\nIBM hours:")
    print(ibm["hour"].describe())


# Run the main workflow only when this file is executed directly.
if __name__ == "__main__":
    main()


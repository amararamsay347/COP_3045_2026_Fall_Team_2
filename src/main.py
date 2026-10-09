from pathlib import Path
import sys

# Resolve the project root so the script can find data files and package imports reliably.
PROJECT_DIR = Path(__file__).resolve().parents[1]

# Allow the project package to be imported when this script is run directly.
if __package__ in (None, ""):
    sys.path.insert(0, str(PROJECT_DIR))

# Import the dataset inspection and cleaning functions used by the main workflow.
from src.data_processing import clean_ibm, clean_paysim, inspect_paysim


# Store the dataset paths in one place so they are easy to update later.
PAYSIM_FILE = PROJECT_DIR / "data" / "PS_20174392719_1491204439457_log.csv"
IBM_FILE = PROJECT_DIR / "data" / "HI-Small_Trans.csv"


def main():
    # Inspect a sample of the raw PaySim CSV.
    inspect_paysim(PAYSIM_FILE)

    print("\n" + "=" * 50 + "\n")

    # Clean the PaySim dataset by keeping the fields needed for analysis
    # and creating the derived balance and time variables.
    paysim = clean_paysim(PAYSIM_FILE)

    # Clean the IBM transaction dataset by selecting the important fields,
    # converting timestamps, and creating derived variables.
    ibm = clean_ibm(IBM_FILE)

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


# Run the main workflow only when this file is executed directly.
if __name__ == "__main__":
    main()
from pathlib import Path
import sys

# Resolve the project root so the script can find data files and package imports reliably.
PROJECT_DIR = Path(__file__).resolve().parents[1]

# Allow the project package to be imported when this script is run directly.
if __package__ in (None, ""):
    sys.path.insert(0, str(PROJECT_DIR))

# Import the dataset inspection and cleaning functions used by the main workflow.
from src.data_processing import clean_ibm, clean_paysim, combine_datasets, inspect_paysim


# Store the dataset paths in one place so they are easy to update later.
PAYSIM_FILE = PROJECT_DIR / "data" / "paysim_data.csv"
IBM_FILE = PROJECT_DIR / "data" / "HI-Small_Trans.csv"
PROCESSED_DIR = PROJECT_DIR / "data" / "processed"
CLEAN_DATA_FILE = PROJECT_DIR / "03-Data cleaning" / "clean_data.csv"


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

    print(f"\nCleaned PaySim dataset saved to: {paysim_output}")
    print(f"Cleaned IBM dataset saved to: {ibm_output}")

    # Export the combined cleaned data required by the graphical EDA assignment.
    df = combine_datasets(paysim, ibm)
    CLEAN_DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(CLEAN_DATA_FILE, index=False, chunksize=100_000)
    print(f"\nCombined cleaned dataset saved to: {CLEAN_DATA_FILE}")


# Run the main workflow only when this file is executed directly.
if __name__ == "__main__":
    main()

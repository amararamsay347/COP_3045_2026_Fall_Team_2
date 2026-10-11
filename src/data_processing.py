import pandas as pd
from pathlib import Path


# Review a sample of the PAYSim data to inspect schema, types, missing values, and duplicates.
def inspect_paysim(file_path):
    paysim = pd.read_csv(file_path, nrows=5000)

    print("PAYSim head: ")
    print(paysim.head())

    print("\nPAYSim columns: ")
    print(paysim.columns)

    print("\nPAYSim Data Type")
    print(paysim.dtypes)

    print("\nPAYSim Missing Values")
    print(paysim.isna().sum())

    print("\nDuplicates: ")
    print(paysim.duplicated().sum())

    print("\nShape: ")
    print(paysim.shape)


# Inspect each IBM CSV file in a folder and print a summary of its structure and data quality.
def inspect_ibm(folder_path):

    folder = Path(folder_path)

    files = list(folder.glob("*.csv"))

    for file in files:

        print("\n" + "=" * 60)
        print(f"FILE: {file.name}")
        print("=" * 60)

        df = pd.read_csv(file, nrows=5000)

        print("IBM head: ")
        print(df.head())

        print("\nIBM columns: ")
        print(df.columns)

        print("\nIBM Data Type")
        print(df.dtypes)

        print("\nIBM Missing Values")
        print(df.isna().sum())

        print("\nDuplicates: ")
        print(df.duplicated().sum())

        print("\nShape: ")
        print(df.shape)


# Keep only the relevant PAYSim fields and create derived features useful for fraud detection.
def clean_paysim(file_path):
    # Select the columns needed for analysis and reduce memory use for the dataset.
    columns = ["step",
               "type",
               "amount",
               "oldbalanceOrg",
               "newbalanceOrig",
               "oldbalanceDest",
               "newbalanceDest",
               "isFraud"]

    df = pd.read_csv(file_path, usecols=columns)

    # Standardize transaction labels so the values are consistent and easy to compare.
    df["type"] = df["type"].str.strip().str.upper()

    # Add the hour of the transaction to help detect time-based fraud patterns.
    df["hour"] = df["step"] % 24

    # Calculate how much each account balance changed during a transaction.
    df["origin_balance_change"] = df["newbalanceOrig"] - df["oldbalanceOrg"]

    # Measure the recipient-side balance shift to reveal suspicious transfers.
    df["destination_balance_change"] = df["newbalanceDest"] - df["oldbalanceDest"]

    return df


# Select the primary IBM fields and normalize values so the financial records are easier to analyze.
def clean_ibm(file_path):

    # Keep only the columns most relevant to laundering detection and payment pattern analysis.
    columns = [
        "Timestamp",
        "From Bank",
        "To Bank",
        "Amount Received",
        "Receiving Currency",
        "Amount Paid",
        "Payment Currency",
        "Payment Format",
        "Is Laundering"
    ]

    df = pd.read_csv(file_path, usecols=columns)

    # Convert timestamps to a proper datetime type for time-based analysis.
    df["Timestamp"] = pd.to_datetime(df["Timestamp"])

    # Normalize currency strings to uppercase for consistent comparisons.
    df["Receiving Currency"] = df["Receiving Currency"].str.strip().str.upper()
    df["Payment Currency"] = df["Payment Currency"].str.strip().str.upper()
    df["Payment Format"] = df["Payment Format"].str.strip().str.upper()

    # Add derived time and relationship features to support pattern analysis.
    df["hour"] = df["Timestamp"].dt.hour
    df["Same Bank"] = df["From Bank"] == df["To Bank"]

    return df


def combine_datasets(paysim, ibm):
    # Add comparable analysis fields while preserving each dataset's original columns.
    paysim_analytics = paysim.copy()
    paysim_analytics["dataset_source"] = "PAYSim"
    paysim_analytics["transaction_amount"] = paysim["amount"]
    paysim_analytics["currency"] = pd.NA
    paysim_analytics["transaction_category"] = paysim["type"]
    paysim_analytics["is_suspicious"] = paysim["isFraud"]
    paysim_analytics["label_type"] = "fraud"

    ibm_analytics = ibm.copy()
    ibm_analytics["dataset_source"] = "IBM"
    ibm_analytics["transaction_amount"] = ibm["Amount Received"]
    ibm_analytics["currency"] = ibm["Receiving Currency"]
    ibm_analytics["transaction_category"] = ibm["Payment Format"]
    ibm_analytics["is_suspicious"] = ibm["Is Laundering"]
    ibm_analytics["label_type"] = "laundering"

    return pd.concat(
        [paysim_analytics, ibm_analytics],
        ignore_index=True,
        sort=False,
    )

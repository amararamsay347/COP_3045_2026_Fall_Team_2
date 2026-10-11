# COP_3045_2026_Fall_Team_2

# Data Processing

This branch contains the data processing workflow for our financial fraud and money laundering analysis project. It includes two Python files: `data_processing.py` and `main.py`.

## Files

### 1. `data_processing.py`

Contains functions for inspecting, cleaning, and combining the PAYSim and IBM datasets.

**Data Inspection**
- `inspect_paysim()`: Examines the first 5,000 PAYSim records, including columns, data types, missing values, duplicates, and dataset shape.
- `inspect_ibm()`: Performs the same inspection for each IBM CSV file in the specified folder.

**Data Cleaning**
- `clean_paysim()`: Selects relevant transaction columns, standardizes transaction types, and creates additional features such as transaction hour and account balance changes.
- `clean_ibm()`: Selects relevant financial columns, converts timestamps to datetime, standardizes currencies and payment formats, and creates transaction hour and same-bank indicators.

**Dataset Combination**
- `combine_datasets()`: Combines both cleaned datasets into a single analytical dataset using `pd.concat()`.
- Creates common columns such as `transaction_amount`, `currency`, `transaction_category`, and `is_suspicious`.
- Preserves the original columns and identifies each record's source and label type.

### 2. `main.py`

Serves as the main entry point for the data processing workflow.

- Imports and executes the functions from `data_processing.py`.
- Inspects and cleans both datasets.
- Displays cleaned data previews and dataset dimensions.
- Generates summary statistics for fraud labels, laundering labels, transaction categories, and transaction hours.
- Combines both datasets into one analytical dataset.
- Exports the final dataset to `data/processed/combined_transactions.csv`.

## How to Run

From the project root directory, run:

```bash
python -m src.main
```

**Requirements:**
- Python 3
- Pandas
- Original PAYSim and IBM CSV files in their expected directories.

## Output

The workflow generates:

`data/processed/combined_transactions.csv`

This file contains the combined financial transactions, standardized analytical fields, derived features, and suspicious transaction labels.

**Note:** PAYSim identifies fraudulent transactions, while IBM identifies money laundering. The `label_type` column preserves this distinction.

## Purpose

The goal of this branch is to prepare both datasets for exploratory data analysis (EDA), transaction pattern comparisons, and further investigation of suspicious financial activity.

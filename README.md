# COP3045 Fall 2026 - Team 2

## Project Overview

This project analyzes synthetic financial transaction data from PAYSim (fraud detection) and IBM HI-Small (money laundering detection). The application cleans and combines the datasets, performs exploratory data analysis (EDA), generates visualizations, and produces an automated PDF report.

## Data Processing

The data-processing workflow is implemented in two Python files: `src/data_processing.py` and `src/main.py`.

### 1. data_processing.py

Contains reusable functions and an object-oriented class for inspecting, cleaning, and combining the datasets.

**Data Loading and Validation**

- `load_csv()`: Loads CSV files with file-existence checks, column validation, and exception handling.
- `display_dataset_info()`: Displays dataset previews, columns, data types, missing values, duplicates, and dimensions.

**Data Inspection**

- `inspect_paysim()`: Inspects the first 5,000 PAYSim records.
- `inspect_ibm()`: Inspects the first 5,000 records of each IBM CSV file in the specified folder.

**Data Cleaning**

- `clean_paysim()`: Standardizes transaction types and calculates transaction hours and account balance changes.
- `clean_ibm()`: Converts timestamps, standardizes currencies and payment formats, and creates transaction-hour and same-bank indicators.

**Dataset Combination**

- `combine_datasets()`: Combines both datasets using `pd.concat()`, creates standardized analytical columns, and preserves the original transaction fields.

**Object-Oriented Programming**

The `TransactionDataProcessor` class coordinates the data-processing workflow.

- `__init__()`: Initializes dataset paths and internal attributes.
- `inspect_data()`: Inspects the input datasets.
- `clean_data()`: Cleans and stores both datasets.
- `get_cleaned_data()`: Returns copies of the cleaned datasets.
- `combine_data()`: Combines the cleaned datasets into one analytical DataFrame.

The class uses encapsulation to manage the cleaned data internally.

### 2. main.py

Serves as the entry point for the data-processing workflow.

- Locates the PAYSim and IBM CSV files.
- Initializes and uses the `TransactionDataProcessor` class.
- Inspects and cleans the transaction datasets.
- Displays dataset previews and summary statistics.
- Exports the individual cleaned datasets.
- Generates the combined analytical dataset for further analysis.

## Datasets

Place the original CSV files in the following locations:

- PAYSim: `data/paysim_data.csv`
- IBM: `data/HI-Small_Trans.csv`

The application also supports these alternate locations:

- `data/ibm/paysim_data.csv`
- `data/IBM_small_HI_data/HI-Small_Trans.csv`

## Setup and Run

Create the Conda environment:

```bash
conda env create -f environment.yml
```

Activate the environment:

```bash
conda activate cop3045
```

Run the complete application:

```bash
python run_all.py
```

To execute only the data-processing workflow:

```bash
python -m src.main
```

## Outputs

The data-processing workflow generates:

- `data/processed/paysim_cleaned.csv`
- `data/processed/ibm_cleaned.csv`
- `03-Data cleaning/clean_data.csv`

The full application also generates:

- EDA charts: `04-EDA/output/`
- PDF report: `05-Report/project_report.pdf`

To regenerate the PDF report after the required data and charts are available:

```bash
python 05-Report/generate_report.py
```

## Purpose

The project aims to identify and compare suspicious financial transaction patterns across the two datasets.

PAYSim identifies fraudulent transactions, while IBM identifies money laundering. The `label_type` column preserves this distinction.

The refactored application improves maintainability through reusable functions, type hints, docstrings, input validation, exception handling, and object-oriented programming.

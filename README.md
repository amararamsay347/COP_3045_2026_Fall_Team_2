# COP_3045_2026_Fall_Team_2

## Overview

This project cleans and analyzes PaySim synthetic fraud data and IBM HI-Small
synthetic money-laundering data. It combines the cleaned transactions for
exploratory analysis and generates charts and a PDF report.

## Datasets

Download link for the **PAYSIM** 'Synthetic Finanical Datasets for Fraud Detection':
[PAYSIM Synthetic Finanical Datasets for Fraud Detection](https://www.kaggle.com/datasets/ealaxi/paysim1)

The IBM HI-Small transaction dataset is already included in the repository at
`data/ibm/IBM_small_HI_data/HI-Small_Trans.csv`.

The pipeline looks for datasets in these default locations:

- `data/paysim_data.csv`
- `data/HI-Small_Trans.csv`

Or in the alternate locations:

- `data/ibm/paysim_data.csv`
- `data/ibm/IBM_small_HI_data/HI-Small_Trans.csv`

## Setup

Create and activate the Conda environment from the project root:

```bash
conda env create -f environment.yml
conda activate cop3045
```

If the environment already exists, activate it.

## Run the project

From the project root, run the full workflow:

```bash
python run_all.py
```

The workflow cleans both datasets, produces summary statistics, generates
exploratory data analysis charts, and creates the PDF report. To regenerate
just the report after the cleaned data is available, run:

```bash
python 05-Report/generate_report.py
```

## Outputs

- Cleaned PaySim data: `data/processed/paysim_cleaned.csv`
- Cleaned IBM data: `data/processed/ibm_cleaned.csv`
- Combined data: `03-Data cleaning/clean_data.csv`
- EDA charts: `04-EDA/output/`
- PDF report: `05-Report/project_report.pdf`

PaySim labels fraudulent transactions, while IBM labels money-laundering
transactions. The combined data preserves the source and label type so results
from the two datasets can be interpreted separately.

## Project structure

- `run_all.py` runs the full workflow in order.
- `src/data_processing.py` cleans and combines the transaction datasets.
- `src/main.py` runs data cleaning and exports the cleaned and combined data.
- `src/summary_statistics.py` produces summary statistics.
- `04-EDA/` contains the graphical EDA workflow and chart output.
- `05-Report/` contains the PDF report generator and report output.

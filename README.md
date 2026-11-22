# COP_3045_2026_Fall_Team_2

## Overview

This project cleans and analyzes PaySim synthetic fraud data and IBM HI-Small
synthetic money-laundering data. It combines the cleaned transactions for
exploratory analysis and generates charts and a PDF report.

## Why combine the Datasets?

Concatenating the datasets is appropriate for a shared exploratory workflow becase both contain transaction-level records, and selected fields can be mapped to common analysis columns such as transaction amount, category, and a binary suspicious flag. Concatenation only oppends the records, it does not claim that transactions in one dataset match transactions in the other. 

The combined data preserves `dataset_source` and `label_type`, such that PaySim fraud labels remain distinct from IBM money-laundering labels remain distinct from the IBM money-laundering labels. The datasets have different label definitions, features, and currencies, so their raw amounts and suspicious rates should not be treated as directly interchangeable. This is how the combination is implemented in the src/data_processing.py. 

## Datasets

Download link for the **PAYSIM** 'Synthetic Finanical Datasets for Fraud Detection' Dataset:
[PAYSIM Synthetic Finanical Datasets for Fraud Detection](https://www.kaggle.com/datasets/ealaxi/paysim1)

Download link for the **IBM Transactions (HI-Small_Trans.csv)** Dataset:
[IBM Transactions for Anti Money Laundering (HI-Small_Trans.csv)](https://www.kaggle.com/datasets/ealtman2019/ibm-transactions-for-anti-money-laundering-aml?select=HI-Small_Trans.csv)

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

## Project structure

The src/ package separates CSV loading, preprocessing, summary statistics, exploratory data analysis, and PDF reporting into individual modules. src/paths.py defines the shared input and output locations, and run_all.py runs the pipeline stages in order.

## Cleaning preparation

The program counts and keeps missing non label values and repeated rows because distinct transactions can match across the selected fields. Missing files or required columns, empty datasets, invalid labels, nonnumeric or infinite values in checked fields, and malformed IBM timestamps stop the run. Transaction types, currencies, and payment formats are trimmed and uppercased, while balance changes and same bank indicators are derived from the source fields.


## Outputs

- Cleaned PaySim data: `data/processed/paysim_cleaned.csv`
- Cleaned IBM data: `data/processed/ibm_cleaned.csv`
- Combined data: `03-Data cleaning/clean_data.csv`
- EDA charts: `04-EDA/output/`
- PDF report: `05-Report/project_report.pdf`

PaySim labels fraudulent transactions, while IBM labels money-laundering
transactions. The combined data preserves the source and label type so results
from the two datasets can be interpreted separately.

## EDA findings and interpretation

- **The labels are rare in both datasets.** PaySim has 8,213 fraud-labeled
  transactions out of 6,362,620 (about 0.129%); IBM has 5,177
  laundering-labeled transactions out of 5,078,345 (about 0.102%). These are
  highly imbalanced datasets, so overall accuracy or raw counts alone would
  hide how rarely the positive labels occur. The label meanings differ, so
  these rates are descriptive within each source, not a direct comparison of
  equivalent outcomes.
- **Category rates and category counts tell different stories.** PaySim
  transfers have the highest fraud rate (0.7688%; 4,097 of 532,909), while
  cash-outs have a lower rate (0.1840%) but slightly more fraud-labeled
  transactions (4,116) because there are many more cash-outs. In IBM, ACH has
  the highest laundering rate (0.7462%; 4,483 of 600,797). These are observed
  rates in the supplied synthetic data, not evidence that a category causes
  fraud or laundering.
- **The amount and time charts need context.** IBM amounts are shown in native
  currencies, which are not converted and cannot be compared directly across
  currencies. The daily charts show uneven transaction volume, not daily
  suspicious rates; gaps or drops reflect the supplied data's coverage and do
  not by themselves indicate a change in risk. The PaySim amount/balance chart
  uses a random sample of 5,000 positive-amount rows. Its few fraud-labeled
  points suggest patterns to investigate, but the sparse positives and overlap
  with non-fraud records do not establish a reliable detection rule.
- **The auxiliary charts count metadata records.** The laundering-pattern
  chart counts rows in `HI-Small_Patterns.csv`, and the entity-type chart
  counts IBM account-registry records. These counts do not show transaction
  prevalence or establish that a pattern or entity type is associated with
  laundering.

## Project structure

- `run_all.py` runs the full workflow in order.
- `src/data_processing.py` cleans and combines the transaction datasets.
- `src/main.py` runs data cleaning and exports the cleaned and combined data.
- `src/summary_statistics.py` produces summary statistics.
- `04-EDA/` contains the graphical EDA workflow and chart output.
- `05-Report/` contains the PDF report generator and report output.

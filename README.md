# COP3045 Fall 2026 - Team 2

This project cleans and analyzes PaySim fraud data and IBM HI-Small-Transaction data.
It produces summary statistics and charts showing
transaction amounts, transaction types, daily activity, and the relationship
between PaySim transaction amounts and account balance changes.

## Datasets

Download and extract both datasets, then place the CSVs in `data/`:

- [PaySim](https://www.kaggle.com/datasets/ealaxi/paysim1): rename `PS_20174392719_1491204439457_log.csv` to `paysim_data.csv`.
- [IBM AML](https://www.kaggle.com/datasets/ealtman2019/ibm-transactions-for-anti-money-laundering-aml): use `HI-Small_Trans.csv`.

Raw and generated CSVs are ignored by Git.

## Setup

Run from the project folder:

```bash
conda env create -f environment.yml
conda activate cop3045
```

For an existing environment, use `conda env update -f environment.yml --prune` instead of creating it.

## Run

```bash
python src/main.py
python src/summary_statistics.py
python "04-EDA/graphical_eda.py"
```

## Outputs

- Cleaned CSVs: `data/processed/` and `03-Data cleaning/clean_data.csv`.
- Charts: `04-EDA/output/`.

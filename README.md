# COP3045 Fall 2026 - Team 2

Cleans and analyzes PaySim (fraud) and IBM HI-Small (money-laundering) transaction data, then generates a PDF report.

## Datasets
Place these in `data/` (ignored by Git):
- PaySim: rename the CSV to `paysim_data.csv`
- IBM AML: `HI-Small_Trans.csv`

## Setup and run

Create and activate the project environment before running the pipeline:

```bash
conda env create -f environment.yml
conda activate cop3045
python run_all.py
```

If the `cop3045` environment already exists, update it after changing the
dependencies:

```bash
conda env update -f environment.yml --prune
conda activate cop3045
python run_all.py
```

`run_all.py` uses the `cop3045` Conda environment even when launched from a
different active Python environment. It checks for required packages and gives
an actionable update command if the environment is missing dependencies.

## Outputs
- Cleaned data: `03-Data cleaning/clean_data.csv`
- Charts: `04-EDA/output/`
- Report: `05-Report/project_report.pdf`

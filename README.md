# COP3045 Fall 2026 - Team 2

Cleans and analyzes PaySim (fraud) and IBM HI-Small (money-laundering) transaction data, then generates a PDF report.

## Datasets
Place these in `data/` (ignored by Git):
- PaySim: rename the CSV to `paysim_data.csv`
- IBM AML: `HI-Small_Trans.csv`

## Setup and run
conda env create -f environment.yml
conda activate cop3045
python run_all.py

## Outputs
- Cleaned data: `03-Data cleaning/clean_data.csv`
- Charts: `04-EDA/output/`
- Report: `05-Report/project_report.pdf`

# COP_3045_2026_Fall_Team_2

## Generate the automated report

From the project root, install the project environment and run the data pipeline
before generating the PDF:

```powershell
conda env create -f environment.yml
conda activate cop3045
python src/main.py
python 05-Report/generate_report.py
```

The pipeline writes cleaned datasets and `data/processed/combined_transactions.csv`.
The report reads that combined dataset and writes the PDF and chart images to
`05-Report/`.
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

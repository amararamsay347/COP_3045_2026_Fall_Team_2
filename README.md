# COP3045 Fall 2026 - Team 2

Cleans and analyzes PaySim (fraud) and IBM HI-Small (money-laundering) transaction data, then generates a PDF report. The two datasets are combined into one analytical table because both are synthetic financial-transaction data with fraud/laundering labels, which lets us compare suspicious-transaction patterns across sources.

## Datasets
Place the raw CSVs at `data/paysim_data.csv` and `data/HI-Small_Trans.csv`.
The pipeline also accepts the existing download locations
`data/ibm/paysim_data.csv` and `data/IBM_small_HI_data/HI-Small_Trans.csv`.

## Setup and run

```bash
conda env create -f environment.yml
conda activate cop3045
python run_all.py
```

If the `cop3045` environment already exists, start with `conda activate cop3045`.
To rebuild just the PDF and its charts after cleaning, run
`python 05-Report/generate_report.py`. The report and graphical EDA read the
same combined CSV at `03-Data cleaning/clean_data.csv`.

## Outputs
- Cleaned data: `03-Data cleaning/clean_data.csv`
- Charts: `04-EDA/output/`
- Report: `05-Report/project_report.pdf`

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
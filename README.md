# COP3045 Fall 2026 - Team 2

Cleans and analyzes PaySim synthetic fraud data and IBM HI-Small synthetic
money-laundering data, then generates analysis outputs and a PDF report.

## Generate the full workflow

From the project root:

```powershell
conda env create -f environment.yml
conda activate cop3045
python run_all.py
```

The workflow prepares the datasets, runs summary statistics and graphical EDA,
and generates the PDF report.

## Generate only the report

After the combined dataset is available at
`03-Data cleaning/clean_data.csv`, run:

```powershell
python 05-Report/generate_report.py
```

The report command also accepts an alternate combined CSV, output directory,
and PDF name:

```powershell
python 05-Report/generate_report.py --data path/to/combined.csv --output-dir path/to/output --report-name report.pdf
```

The report implementation is organized in `src/reporting/`. Its
`ReportApplication` class can be reused with another compatible combined CSV.

## Outputs

- Combined data: `03-Data cleaning/clean_data.csv`
- EDA charts: `04-EDA/output/`
- PDF report and report charts: `05-Report/`

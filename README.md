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
and generates the PDF report. If the `cop3045` environment already exists,
activate it instead of creating it again.

## Generate only the report

After the combined dataset has been prepared at
`03-Data cleaning/clean_data.csv`, run:

```powershell
python 05-Report/generate_report.py
```

This creates `project_report.pdf` and three charts in `05-Report/`:

- `suspicious_rate_by_source.png`
- `suspicious_rate_by_category.png`
- `median_amount_by_status.png`

The report command accepts an alternate combined CSV, output directory, and
PDF name:

```powershell
python 05-Report/generate_report.py --data path/to/combined.csv --output-dir path/to/output --report-name report.pdf
```

Use `python 05-Report/generate_report.py --help` to see all options. The
reporting implementation is organized in `src/reporting/`; its
`ReportApplication` class can be reused with another CSV containing the
required transaction fields.

## Outputs

- Combined data: `03-Data cleaning/clean_data.csv`
- EDA charts: `04-EDA/output/`
- PDF report and report charts: `05-Report/`

## Validate automated reporting

Run the reporting integration test from the project root:

```powershell
python -m pytest src/reporting/test_reporting.py -q
```

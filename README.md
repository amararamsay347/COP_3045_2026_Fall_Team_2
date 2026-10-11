# COP_3045_2026_Fall_Team_2

## Set up the Conda environment

Create the environment from the repository's `environment.yml` file and activate it:

```bash
conda env create -f environment.yml
conda activate cop3045
```

If you update the dependencies in `environment.yml`, apply the changes with:

```bash
conda env update -f environment.yml --prune
```

## Create cleaned data and compute summary statistics

Run the data-cleaning workflow first from the project folder. It saves the cleaned
PaySim and IBM datasets under `data/processed/` and exports the combined cleaned
transactions to `03-Data cleaning/clean_data.csv`:

```bash
python src/main.py
```

Then calculate summary statistics from those cleaned datasets:

```bash
python src/summary_statistics.py
```

The generated cleaned CSV files are ignored by Git.

## Graphical exploratory data analysis

After updating the Conda environment and running the cleaning workflow above,
run the EDA script manually:

```bash
python "04-EDA/graphical_eda.py"
```

The script reads `03-Data cleaning/clean_data.csv` into `df` and saves four
transaction charts in `04-EDA/output/`:

- Received-amount distributions for the six most common IBM currencies, in
  native units on a logarithmic scale. Non-positive amounts are omitted and
  outlier markers are hidden.
- Transaction counts by category, with separate PAYSim and IBM panels.
- PAYSim transaction amounts versus origin balance changes, using a reproducible
  random sample of up to 5,000 rows and a fraud-status legend.
- Daily transaction counts, with PAYSim simulation days and IBM recorded dates.

The account registry and laundering-pattern CSVs in
`data/ibm/IBM_small_HI_data/` provide two optional supplementary charts.
Pattern counts describe transaction rows in the pattern CSV, grouped by pattern
family. These supplementary files are not required to produce the four
transaction charts.

All data paths are resolved from the scripts' locations. A missing cleaned CSV
produces a message asking you to run `src/main.py` first.

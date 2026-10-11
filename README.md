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

## Create the combined dataset and compute summary statistics

Run the data-cleaning workflow first. It cleans the PaySim and IBM transaction
datasets, then saves their combined analytical data to
`data/processed/combined_transactions.csv`:

```bash
python src/main.py
```

Then calculate numerical and categorical summary statistics from the combined
dataset:

```bash
python src/summary_statistics.py
```

The generated files in `data/processed/` are ignored by Git.
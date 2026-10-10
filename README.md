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

Run the data-cleaning workflow first. It saves the cleaned PaySim and IBM datasets
under `data/processed/`:

```bash
python src/main.py
```

Then calculate summary statistics from those cleaned datasets:

```bash
python src/summary_statistics.py
```

The generated files in `data/processed/` are ignored by Git.
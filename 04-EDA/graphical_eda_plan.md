# Graphical EDA implementation plan

Status: Approved by the user and implemented. Python execution remains manual.

The supplied assignment requires reading `03-Data cleaning/clean_data.csv`
into a pandas DataFrame named `df`, using Matplotlib and Seaborn, and creating
at least three informative, clearly labelled visualizations. It requires
approval of the plan before implementation and leaves Python execution to
the user.

The existing `04-EDA/graphical_eda.py` reads and cleans raw files instead.
The required cleaned CSV does not exist in this checkout. The current
`src/main.py` also references an IBM transaction file path that does not
match the file in `data/HI-Small_Trans.csv`.

Proposed changes:

1. Update the existing cleaning workflow in `src/main.py` to use the actual
   IBM transaction file and export the combined cleaned transactions to
   `03-Data cleaning/clean_data.csv`, using `combine_datasets`. Retain its
   separate cleaned outputs used by `src/summary_statistics.py`.
2. Make `04-EDA/graphical_eda.py` read that cleaned CSV as `df`. Resolve
   paths relative to the script, validate the necessary columns, and
   give a clear message if the cleaned file is missing.
3. Generate these charts from the cleaned transaction data:
   - IBM received-amount box plots for the six most common currencies.
     Label the logarithmic scale and native currency units; explain
     that non-positive values are omitted and outlier markers are hidden.
   - Transaction counts by category in separate PAYSim and IBM panels.
   - A reproducible sample of PAYSim transaction amounts versus origin
     balance changes, with a fraud-status legend. Keep PAYSim amounts
     separate from the IBM currencies.
   - Daily transaction counts, using simulation days for PAYSim and
     recorded dates for IBM. Remove the invented PAYSim calendar dates.
4. Keep the existing account and laundering-pattern charts as optional
   supplements. Group pattern variants into their named families and
   consistently label the counted pattern CSV rows as transactions.
   Add count labels so small account categories remain readable.
5. Declare Matplotlib and Seaborn in `environment.yml`, document the
   manual cleaning and EDA commands in `README.md`, and ignore the
   generated cleaned CSV in `.gitignore`.

Static review checked the cleaned-data path and required columns against
`combine_datasets`, all four primary chart calls, titles and axis labels,
the scatter-plot legend, and optional metadata handling. No Python code was
executed and no updated charts were generated during implementation.

Run `python src/main.py` manually to create the cleaned CSV, followed by
`python "04-EDA/graphical_eda.py"` to save charts to `04-EDA/output/`.
The existing PNGs represent the previous implementation until that run.

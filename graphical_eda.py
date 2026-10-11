
#EDA for the two datasets, IBM Small HI data and Paysim data
#Using visualizations copilot suggested: transaction counts by pattern, daily transaction volume, received-amount distributions by currency, and account records by entity type
#Summary tables copilot suggested: for transaction and account profiles, missing values, laundering patterns, native-currency amounts, and account entity types.

#Import libraries and load datasets
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

project_dir = Path.cwd()
data_dir = project_dir / "data" / "ibm" / "IBM_small_HI_data"
while not data_dir.is_dir() and project_dir != project_dir.parent:
    project_dir = project_dir.parent
    data_dir = project_dir / "data" / "ibm" / "IBM_small_HI_data"
if not data_dir.is_dir():
    raise FileNotFoundError("Could not find data/ibm/IBM_small_HI_data from the notebook directory or its parents.")

ibm_data = pd.read_csv(data_dir / "HI-Small_Patterns.csv")
print(f"Loaded IBM pattern data from: {data_dir / 'HI-Small_Patterns.csv'}")
paysim_file = project_dir / "data" / "paysim_data.csv"
if not paysim_file.is_file():
    raise FileNotFoundError(f"PaySim data file not found: {paysim_file}. Place paysim_data.csv in the project's data folder.")
paysim_data = pd.read_csv(paysim_file)
print(f"Loaded PaySim data from: {paysim_file}")

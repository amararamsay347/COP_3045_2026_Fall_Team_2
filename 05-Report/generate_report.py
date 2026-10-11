# Import pandas to read and analyze the cleaned datasets.
import pandas as pd

# Import Matplotlib and Seaborn to create the report visualizations.
import matplotlib.pyplot as plt
import seaborn as sns

# Import FPDF to build and save the PDF report.
from fpdf import FPDF


# ------------------------------------------------------------
# FILE PATHS
# ------------------------------------------------------------

# These are the cleaned datasets created by the data preparation part
# of the project.
paysim_file = "data/processed/paysim_cleaned.csv"
ibm_file = "data/processed/ibm_cleaned.csv"

# This is the PDF file that this script will create.
report_file = "05-Report/project_report.pdf"

# These image files will store the graphs before they are added
# to the PDF report.
chart1_file = "05-Report/paysim_type_rates.png"
chart2_file = "05-Report/ibm_format_rates.png"
chart3_file = "05-Report/hourly_rates.png"


# ------------------------------------------------------------
# READ DATASET INFORMATION
# ------------------------------------------------------------

# Read only the first row of each file to determine how many
# variables are in each cleaned dataset.
paysim_header = pd.read_csv(paysim_file, nrows=0)
ibm_header = pd.read_csv(ibm_file, nrows=0)

paysim_columns = len(paysim_header.columns)
ibm_columns = len(ibm_header.columns)


# ------------------------------------------------------------
# READ THE CLEANED DATASETS
# ------------------------------------------------------------

# Only load the columns needed for the report.
# This reduces memory use because both datasets contain millions of rows.
paysim = pd.read_csv(
    paysim_file,
    usecols=[
        "type",
        "amount",
        "isFraud",
        "hour"
    ]
)

ibm = pd.read_csv(
    ibm_file,
    usecols=[
        "Amount Paid",
        "Payment Currency",
        "Payment Format",
        "Is Laundering",
        "hour"
    ]
)

print("Cleaned datasets loaded successfully.")


# ------------------------------------------------------------
# DATASET SUMMARY
# ------------------------------------------------------------

# Count how many transactions are in each dataset.
paysim_rows = len(paysim)
ibm_rows = len(ibm)

# Count legitimate and fraudulent PaySim transactions.
paysim_legitimate = int((paysim["isFraud"] == 0).sum())
paysim_fraud = int((paysim["isFraud"] == 1).sum())

# Calculate the PaySim fraud percentage.
paysim_fraud_rate = paysim_fraud / paysim_rows * 100

# Count legitimate and laundering IBM transactions.
ibm_legitimate = int((ibm["Is Laundering"] == 0).sum())
ibm_laundering = int((ibm["Is Laundering"] == 1).sum())

# Calculate the IBM laundering percentage.
ibm_laundering_rate = ibm_laundering / ibm_rows * 100


# ------------------------------------------------------------
# SUMMARY STATISTICS
# ------------------------------------------------------------

# Calculate basic statistics for PaySim transaction amounts.
paysim_amount_count = paysim["amount"].count()
paysim_amount_mean = paysim["amount"].mean()
paysim_amount_median = paysim["amount"].median()
paysim_amount_min = paysim["amount"].min()
paysim_amount_max = paysim["amount"].max()

# Calculate statistics for PaySim transactions that were marked
# as fraud.
paysim_fraud_amount = paysim[
    paysim["isFraud"] == 1
]["amount"]

paysim_fraud_mean = paysim_fraud_amount.mean()
paysim_fraud_median = paysim_fraud_amount.median()


# IBM contains transactions using several currencies.
# Use US DOLLAR transactions for a simple amount summary so amounts
# from different currencies are not mixed together.
ibm_usd = ibm[
    ibm["Payment Currency"] == "US DOLLAR"
]

ibm_amount_count = ibm_usd["Amount Paid"].count()
ibm_amount_mean = ibm_usd["Amount Paid"].mean()
ibm_amount_median = ibm_usd["Amount Paid"].median()
ibm_amount_min = ibm_usd["Amount Paid"].min()
ibm_amount_max = ibm_usd["Amount Paid"].max()

# Calculate statistics for IBM US DOLLAR transactions that were
# marked as laundering.
ibm_laundering_amount = ibm_usd[
    ibm_usd["Is Laundering"] == 1
]["Amount Paid"]

ibm_laundering_mean = ibm_laundering_amount.mean()
ibm_laundering_median = ibm_laundering_amount.median()


# ------------------------------------------------------------
# PAYSIM CATEGORY SUMMARY
# ------------------------------------------------------------

# Group PaySim transactions by transaction type.
# The mean of a 0/1 label gives the fraud rate for each type.
paysim_type_summary = (
    paysim.groupby("type")["isFraud"]
    .agg(["count", "sum", "mean"])
    .reset_index()
)

# Rename the columns to make their meaning clearer.
paysim_type_summary = paysim_type_summary.rename(
    columns={
        "sum": "fraud_count",
        "mean": "fraud_rate"
    }
)

# Convert the fraud rate from a decimal to a percentage.
paysim_type_summary["fraud_rate"] = (
    paysim_type_summary["fraud_rate"] * 100
)

# Sort the transaction types from highest to lowest fraud rate.
paysim_type_summary = paysim_type_summary.sort_values(
    "fraud_rate",
    ascending=False
)

# Store the PaySim transaction type with the highest fraud rate.
highest_paysim_type = paysim_type_summary.iloc[0]["type"]
highest_paysim_rate = paysim_type_summary.iloc[0]["fraud_rate"]


# ------------------------------------------------------------
# IBM CATEGORY SUMMARY
# ------------------------------------------------------------

# Group IBM transactions by payment format.
# The mean of the 0/1 laundering label gives the laundering rate.
ibm_format_summary = (
    ibm.groupby("Payment Format")["Is Laundering"]
    .agg(["count", "sum", "mean"])
    .reset_index()
)

# Rename the columns so they are easier to understand.
ibm_format_summary = ibm_format_summary.rename(
    columns={
        "sum": "laundering_count",
        "mean": "laundering_rate"
    }
)

# Convert the laundering rate into a percentage.
ibm_format_summary["laundering_rate"] = (
    ibm_format_summary["laundering_rate"] * 100
)

# Sort payment formats from highest to lowest laundering rate.
ibm_format_summary = ibm_format_summary.sort_values(
    "laundering_rate",
    ascending=False
)

# Store the payment format with the highest laundering rate.
highest_ibm_format = ibm_format_summary.iloc[0]["Payment Format"]
highest_ibm_rate = ibm_format_summary.iloc[0]["laundering_rate"]


# ------------------------------------------------------------
# HOURLY SUMMARY
# ------------------------------------------------------------

# Calculate the PaySim fraud rate for every hour.
paysim_hourly = (
    paysim.groupby("hour")["isFraud"]
    .mean()
    .reset_index()
)

paysim_hourly["rate"] = paysim_hourly["isFraud"] * 100

# Calculate the IBM laundering rate for every hour.
ibm_hourly = (
    ibm.groupby("hour")["Is Laundering"]
    .mean()
    .reset_index()
)

ibm_hourly["rate"] = ibm_hourly["Is Laundering"] * 100

# Find the hour with the highest PaySim fraud rate.
highest_paysim_hour_row = paysim_hourly.loc[
    paysim_hourly["rate"].idxmax()
]

highest_paysim_hour = int(
    highest_paysim_hour_row["hour"]
)

highest_paysim_hour_rate = highest_paysim_hour_row["rate"]

# Find the hour with the highest IBM laundering rate.
highest_ibm_hour_row = ibm_hourly.loc[
    ibm_hourly["rate"].idxmax()
]

highest_ibm_hour = int(
    highest_ibm_hour_row["hour"]
)

highest_ibm_hour_rate = highest_ibm_hour_row["rate"]


# ------------------------------------------------------------
# VISUALIZATION 1
# PAYSIM FRAUD RATE BY TRANSACTION TYPE
# ------------------------------------------------------------

# Create a bar chart showing the fraud percentage for each
# PaySim transaction type.
plt.figure(figsize=(8, 5))

sns.barplot(
    data=paysim_type_summary,
    x="type",
    y="fraud_rate"
)

plt.title("PaySim Fraud Rate by Transaction Type")
plt.xlabel("Transaction Type")
plt.ylabel("Fraud Rate (%)")

plt.xticks(rotation=45)

# Make sure labels fit inside the image.
plt.tight_layout()

# Save the graph so it can be inserted into the PDF.
plt.savefig(chart1_file)

# Close the graph to free memory.
plt.close()


# ------------------------------------------------------------
# VISUALIZATION 2
# IBM LAUNDERING RATE BY PAYMENT FORMAT
# ------------------------------------------------------------

# Create a bar chart showing the laundering percentage for each
# IBM payment format.
plt.figure(figsize=(9, 5))

sns.barplot(
    data=ibm_format_summary,
    x="Payment Format",
    y="laundering_rate"
)

plt.title("IBM Laundering Rate by Payment Format")
plt.xlabel("Payment Format")
plt.ylabel("Laundering Rate (%)")

plt.xticks(rotation=45, ha="right")

plt.tight_layout()

# Save the second graph.
plt.savefig(chart2_file)

# Close the graph after saving it.
plt.close()


# ------------------------------------------------------------
# VISUALIZATION 3
# SUSPICIOUS TRANSACTION RATE BY HOUR
# ------------------------------------------------------------

# Create a line chart comparing the hourly fraud rate in PaySim
# with the hourly laundering rate in IBM.
plt.figure(figsize=(10, 6))

sns.lineplot(
    data=paysim_hourly,
    x="hour",
    y="rate",
    marker="o",
    label="PaySim Fraud"
)

sns.lineplot(
    data=ibm_hourly,
    x="hour",
    y="rate",
    marker="o",
    label="IBM Laundering"
)

plt.title("Suspicious Transaction Rate by Hour")
plt.xlabel("Hour")
plt.ylabel("Suspicious Rate (%)")

plt.tight_layout()

# Save the third graph.
plt.savefig(chart3_file)

# Close the graph after saving it.
plt.close()


# ------------------------------------------------------------
# CREATE AUTOMATIC FINDINGS
# ------------------------------------------------------------

# These sentences are created using values calculated directly
# from the cleaned datasets.
finding1 = (
    "PaySim contains "
    + f"{paysim_rows:,}"
    + " transactions, with "
    + f"{paysim_fraud:,}"
    + " marked as fraud. This gives an overall fraud rate of "
    + f"{paysim_fraud_rate:.4f}%."
)

finding2 = (
    "The IBM AML dataset contains "
    + f"{ibm_rows:,}"
    + " transactions, with "
    + f"{ibm_laundering:,}"
    + " marked as laundering. This gives an overall laundering rate of "
    + f"{ibm_laundering_rate:.4f}%."
)

finding3 = (
    "The PaySim transaction type with the highest fraud rate was "
    + str(highest_paysim_type)
    + ", with a fraud rate of "
    + f"{highest_paysim_rate:.4f}%."
)

finding4 = (
    "The IBM payment format with the highest laundering rate was "
    + str(highest_ibm_format)
    + ", with a laundering rate of "
    + f"{highest_ibm_rate:.4f}%."
)

finding5 = (
    "The highest PaySim fraud rate by hour occurred at hour "
    + str(highest_paysim_hour)
    + ", while the highest IBM laundering rate occurred at hour "
    + str(highest_ibm_hour)
    + "."
)


# ------------------------------------------------------------
# CREATE THE PDF REPORT
# ------------------------------------------------------------

# Create a new PDF.
pdf = FPDF()

# Automatically create a new page when the current page becomes full.
pdf.set_auto_page_break(
    auto=True,
    margin=15
)

# Add the first page.
pdf.add_page()


# ------------------------------------------------------------
# PROJECT TITLE
# ------------------------------------------------------------

# Add the project title at the beginning of the report.
pdf.set_font(
    "Arial",
    "B",
    16
)

pdf.multi_cell(
    0,
    10,
    "Financial Fraud and Money-Laundering Detection in Transaction Data",
    align="C"
)

pdf.ln(5)


# ------------------------------------------------------------
# DATASET SUMMARY SECTION
# ------------------------------------------------------------

# Add the Dataset Summary heading.
pdf.set_font(
    "Arial",
    "B",
    14
)

pdf.cell(
    0,
    10,
    "1. Dataset Summary",
    ln=True
)

# Use normal text for the dataset information.
pdf.set_font(
    "Arial",
    "",
    11
)

pdf.cell(
    0,
    8,
    "PaySim observations: " + f"{paysim_rows:,}",
    ln=True
)

pdf.cell(
    0,
    8,
    "PaySim variables: " + str(paysim_columns),
    ln=True
)

pdf.cell(
    0,
    8,
    "PaySim fraud transactions: " + f"{paysim_fraud:,}",
    ln=True
)

pdf.cell(
    0,
    8,
    "PaySim fraud rate: " + f"{paysim_fraud_rate:.4f}%",
    ln=True
)

pdf.ln(3)

pdf.cell(
    0,
    8,
    "IBM observations: " + f"{ibm_rows:,}",
    ln=True
)

pdf.cell(
    0,
    8,
    "IBM variables: " + str(ibm_columns),
    ln=True
)

pdf.cell(
    0,
    8,
    "IBM laundering transactions: " + f"{ibm_laundering:,}",
    ln=True
)

pdf.cell(
    0,
    8,
    "IBM laundering rate: " + f"{ibm_laundering_rate:.4f}%",
    ln=True
)


# ------------------------------------------------------------
# SUMMARY STATISTICS SECTION
# ------------------------------------------------------------

# Start a new page for the summary statistics.
pdf.add_page()

pdf.set_font(
    "Arial",
    "B",
    14
)

pdf.cell(
    0,
    10,
    "2. Summary Statistics",
    ln=True
)

# Explain what the table contains.
pdf.set_font(
    "Arial",
    "",
    10
)

pdf.multi_cell(
    0,
    7,
    "IBM amount statistics below use US DOLLAR transactions so values from different currencies are not mixed together."
)

pdf.ln(3)

# Create the header row for the summary statistics table.
pdf.set_font(
    "Arial",
    "B",
    9
)

pdf.cell(45, 8, "Dataset", border=1)
pdf.cell(30, 8, "Count", border=1)
pdf.cell(35, 8, "Mean", border=1)
pdf.cell(35, 8, "Median", border=1)
pdf.cell(35, 8, "Maximum", border=1, ln=True)

# Add the PaySim summary statistics.
pdf.set_font(
    "Arial",
    "",
    9
)

pdf.cell(45, 8, "PaySim", border=1)
pdf.cell(30, 8, f"{paysim_amount_count:,.0f}", border=1)
pdf.cell(35, 8, f"{paysim_amount_mean:,.2f}", border=1)
pdf.cell(35, 8, f"{paysim_amount_median:,.2f}", border=1)
pdf.cell(35, 8, f"{paysim_amount_max:,.2f}", border=1, ln=True)

# Add PaySim fraud-only statistics.
pdf.cell(45, 8, "PaySim Fraud", border=1)
pdf.cell(30, 8, f"{paysim_fraud:,}", border=1)
pdf.cell(35, 8, f"{paysim_fraud_mean:,.2f}", border=1)
pdf.cell(35, 8, f"{paysim_fraud_median:,.2f}", border=1)
pdf.cell(35, 8, "-", border=1, ln=True)

# Add IBM US DOLLAR statistics.
pdf.cell(45, 8, "IBM USD", border=1)
pdf.cell(30, 8, f"{ibm_amount_count:,.0f}", border=1)
pdf.cell(35, 8, f"{ibm_amount_mean:,.2f}", border=1)
pdf.cell(35, 8, f"{ibm_amount_median:,.2f}", border=1)
pdf.cell(35, 8, f"{ibm_amount_max:,.2f}", border=1, ln=True)

# Add IBM laundering-only statistics.
pdf.cell(45, 8, "IBM USD Laundering", border=1)
pdf.cell(30, 8, f"{len(ibm_laundering_amount):,}", border=1)
pdf.cell(35, 8, f"{ibm_laundering_mean:,.2f}", border=1)
pdf.cell(35, 8, f"{ibm_laundering_median:,.2f}", border=1)
pdf.cell(35, 8, "-", border=1, ln=True)


# ------------------------------------------------------------
# VISUALIZATION 1
# ------------------------------------------------------------

# Start a new page and add the first graph.
pdf.add_page()

pdf.set_font(
    "Arial",
    "B",
    14
)

pdf.cell(
    0,
    10,
    "3. Visualizations",
    ln=True
)

pdf.set_font(
    "Arial",
    "B",
    11
)

pdf.cell(
    0,
    8,
    "PaySim Fraud Rate by Transaction Type",
    ln=True
)

pdf.image(
    chart1_file,
    x=20,
    w=170
)


# ------------------------------------------------------------
# VISUALIZATION 2
# ------------------------------------------------------------

# Add the IBM payment-format graph on a new page.
pdf.add_page()

pdf.set_font(
    "Arial",
    "B",
    11
)

pdf.cell(
    0,
    8,
    "IBM Laundering Rate by Payment Format",
    ln=True
)

pdf.image(
    chart2_file,
    x=20,
    w=170
)


# ------------------------------------------------------------
# VISUALIZATION 3
# ------------------------------------------------------------

# Add the hourly comparison graph on a new page.
pdf.add_page()

pdf.set_font(
    "Arial",
    "B",
    11
)

pdf.cell(
    0,
    8,
    "Suspicious Transaction Rate by Hour",
    ln=True
)

pdf.image(
    chart3_file,
    x=15,
    w=180
)


# ------------------------------------------------------------
# KEY ANALYTICAL FINDINGS SECTION
# ------------------------------------------------------------

# Start a new page for the automatically generated findings.
pdf.add_page()

pdf.set_font(
    "Arial",
    "B",
    14
)

pdf.cell(
    0,
    10,
    "4. Key Analytical Findings",
    ln=True
)

pdf.set_font(
    "Arial",
    "",
    11
)

# Add each calculated finding to the PDF.
pdf.multi_cell(
    0,
    8,
    finding1
)

pdf.ln(3)

pdf.multi_cell(
    0,
    8,
    finding2
)

pdf.ln(3)

pdf.multi_cell(
    0,
    8,
    finding3
)

pdf.ln(3)

pdf.multi_cell(
    0,
    8,
    finding4
)

pdf.ln(3)

pdf.multi_cell(
    0,
    8,
    finding5
)


# ------------------------------------------------------------
# SAVE THE PDF
# ------------------------------------------------------------

# Save the completed PDF in the 05-Report folder.
pdf.output(report_file)

# Print a confirmation message after the report is finished.
print("PDF report created successfully.")
print(report_file)
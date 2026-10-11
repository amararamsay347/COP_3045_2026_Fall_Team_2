# Import pandas to read and analyze the combined transaction dataset.
import pandas as pd

# Import Matplotlib and Seaborn to create the report visualizations.
import matplotlib.pyplot as plt
import seaborn as sns

# Import FPDF to automatically build the PDF report.
from fpdf import FPDF


# ------------------------------------------------------------
# FILE PATHS
# ------------------------------------------------------------

# This is the combined analytical dataset created by src/main.py.
data_file = "03-Data cleaning/clean_data.csv"

# This is the final PDF report that this script will create.
report_file = "05-Report/project_report.pdf"

# These image files will temporarily store the visualizations
# before they are inserted into the PDF report.
chart1_file = "05-Report/suspicious_rate_by_source.png"
chart2_file = "05-Report/suspicious_rate_by_category.png"
chart3_file = "05-Report/median_amount_by_status.png"


# ------------------------------------------------------------
# READ THE COMBINED DATASET
# ------------------------------------------------------------

# These are the columns used by the team's combined analytical dataset.
columns = [
    "transaction_amount",
    "currency",
    "transaction_category",
    "dataset_source",
    "label_type",
    "is_suspicious",
]

# Read only the columns needed for the automated report.
# Category and int8 data types help reduce memory usage because
# the combined dataset contains millions of transactions.
df = pd.read_csv(
    data_file,
    usecols=columns,
    dtype={
        "transaction_amount": "float64",
        "currency": "string",
        "transaction_category": "string",
        "dataset_source": "string",
        "label_type": "string",
        "is_suspicious": "int8",
    },
)

print("Combined dataset loaded successfully.")


# ------------------------------------------------------------
# BASIC DATASET INFORMATION
# ------------------------------------------------------------

# Count the total number of transactions.
num_rows = len(df)

# Count the total number of variables used in the analytical dataset.
num_columns = len(df.columns)

# Count how many transactions came from each original dataset.
source_counts = df["dataset_source"].value_counts()

# Count the different label types used in the combined dataset.
label_type_counts = df["label_type"].value_counts()

# Count all legitimate transactions.
not_suspicious_count = int(
    (df["is_suspicious"] == 0).sum()
)

# Count all transactions marked as fraud or laundering.
suspicious_count = int(
    (df["is_suspicious"] == 1).sum()
)

# Calculate the overall percentage of transactions
# marked as suspicious.
overall_suspicious_rate = (
    suspicious_count / num_rows * 100
)


# ------------------------------------------------------------
# DATASET SOURCE SUMMARY
# ------------------------------------------------------------

# Group the combined dataset by its original source.
# The mean of is_suspicious gives the suspicious transaction rate
# because the column contains only 0 and 1.
source_summary = (
    df.groupby(
        "dataset_source",
        observed=True
    )["is_suspicious"]
    .agg(["count", "sum", "mean"])
    .reset_index()
)

# Give the calculated columns clearer names.
source_summary = source_summary.rename(
    columns={
        "count": "transaction_count",
        "sum": "suspicious_count",
        "mean": "suspicious_rate",
    }
)

# Convert the suspicious rate from a decimal into a percentage.
source_summary["suspicious_rate"] = (
    source_summary["suspicious_rate"] * 100
)


# ------------------------------------------------------------
# TRANSACTION CATEGORY SUMMARY
# ------------------------------------------------------------

# Calculate the number of transactions and suspicious rate
# for every transaction category in each dataset.
category_summary = (
    df.groupby(
        [
            "dataset_source",
            "transaction_category",
        ],
        observed=True,
    )["is_suspicious"]
    .agg(["count", "sum", "mean"])
    .reset_index()
)

# Rename the calculated columns.
category_summary = category_summary.rename(
    columns={
        "count": "transaction_count",
        "sum": "suspicious_count",
        "mean": "suspicious_rate",
    }
)

# Convert the suspicious rate into a percentage.
category_summary["suspicious_rate"] = (
    category_summary["suspicious_rate"] * 100
)

# Create a display name containing both the dataset and category.
# This makes it clear which dataset each category belongs to.
category_summary["display_category"] = (
    category_summary["dataset_source"].astype(str)
    + " - "
    + category_summary["transaction_category"].astype(str)
)

# Sort the categories from highest to lowest suspicious rate.
category_summary = category_summary.sort_values(
    "suspicious_rate",
    ascending=False
)


# ------------------------------------------------------------
# FIND THE MAIN CURRENCY FOR EACH DATASET
# ------------------------------------------------------------

# The IBM dataset can contain different currencies.
# Amounts from different currencies should not be treated as though
# they have the same value.

# Count how often each currency appears in each dataset.
currency_counts = (
    df.groupby(
        [
            "dataset_source",
            "currency",
        ],
        observed=True,
    )
    .size()
    .reset_index(name="transaction_count")
)

# Sort so the most common currency appears first for each dataset.
currency_counts = currency_counts.sort_values(
    [
        "dataset_source",
        "transaction_count",
    ],
    ascending=[
        True,
        False,
    ],
)

# Select the most common currency from each dataset.
main_currency_by_source = (
    currency_counts
    .groupby(
        "dataset_source",
        observed=True,
    )
    .first()
    .reset_index()
)


# ------------------------------------------------------------
# TRANSACTION AMOUNT SUMMARY
# ------------------------------------------------------------

# Create an empty list where each dataset's amount statistics
# will be stored.
amount_summary_rows = []

# Create another list for comparing suspicious and
# non-suspicious transaction amounts.
amount_status_rows = []

# Calculate amount statistics separately for each dataset using
# its most common currency.
for row in main_currency_by_source.itertuples(index=False):

    source = row.dataset_source
    currency = row.currency

    # Keep transactions from this dataset and currency.
    source_data = df[
        (df["dataset_source"] == source)
        & (df["currency"] == currency)
    ]

    # Select the transaction amount column.
    amounts = source_data["transaction_amount"].dropna()

    # Store basic numerical summary statistics.
    amount_summary_rows.append(
        {
            "dataset_source": str(source),
            "currency": str(currency),
            "count": amounts.count(),
            "mean": amounts.mean(),
            "median": amounts.median(),
            "minimum": amounts.min(),
            "maximum": amounts.max(),
        }
    )

    # Calculate amount statistics separately for legitimate
    # and suspicious transactions.
    for status in [0, 1]:

        status_amounts = source_data[
            source_data["is_suspicious"] == status
        ]["transaction_amount"].dropna()

        if status == 0:
            status_name = "Not Suspicious"
        else:
            status_name = "Suspicious"

        amount_status_rows.append(
            {
                "dataset_source": str(source),
                "currency": str(currency),
                "status": status_name,
                "count": status_amounts.count(),
                "mean_amount": status_amounts.mean(),
                "median_amount": status_amounts.median(),
            }
        )


# Convert the lists into DataFrames so they can be used
# for tables and visualizations.
amount_summary = pd.DataFrame(
    amount_summary_rows
)

amount_status_summary = pd.DataFrame(
    amount_status_rows
)

# Create a label showing the dataset and currency together.
amount_status_summary["display_source"] = (
    amount_status_summary["dataset_source"]
    + " ("
    + amount_status_summary["currency"]
    + ")"
)


# ------------------------------------------------------------
# KEY ANALYTICAL FINDINGS
# ------------------------------------------------------------

# Find which dataset has the highest suspicious transaction rate.
highest_source_row = source_summary.loc[
    source_summary["suspicious_rate"].idxmax()
]

highest_source = highest_source_row[
    "dataset_source"
]

highest_source_rate = highest_source_row[
    "suspicious_rate"
]

# Find which transaction category has the highest suspicious rate.
highest_category_row = category_summary.iloc[0]

highest_category = highest_category_row[
    "transaction_category"
]

highest_category_source = highest_category_row[
    "dataset_source"
]

highest_category_rate = highest_category_row[
    "suspicious_rate"
]


# ------------------------------------------------------------
# VISUALIZATION 1
# SUSPICIOUS RATE BY DATASET
# ------------------------------------------------------------

# Create a bar chart showing the suspicious transaction rate
# for each original dataset.
plt.figure(
    figsize=(8, 5)
)

sns.barplot(
    data=source_summary,
    x="dataset_source",
    y="suspicious_rate",
)

# Add a title and axis labels.
plt.title(
    "Suspicious Transaction Rate by Dataset"
)

plt.xlabel(
    "Dataset"
)

plt.ylabel(
    "Suspicious Rate (%)"
)

# Adjust spacing so labels fit properly.
plt.tight_layout()

# Save the graph so it can be added to the PDF.
plt.savefig(
    chart1_file,
    dpi=150,
)

# Close the figure to free memory.
plt.close()


# ------------------------------------------------------------
# VISUALIZATION 2
# SUSPICIOUS RATE BY TRANSACTION CATEGORY
# ------------------------------------------------------------

# Create a bar chart comparing suspicious rates across
# the transaction categories in both datasets.
plt.figure(
    figsize=(12, 7)
)

sns.barplot(
    data=category_summary,
    x="display_category",
    y="suspicious_rate",
)

# Add a title and axis labels.
plt.title(
    "Suspicious Transaction Rate by Category"
)

plt.xlabel(
    "Dataset and Transaction Category"
)

plt.ylabel(
    "Suspicious Rate (%)"
)

# Rotate category labels so they remain readable.
plt.xticks(
    rotation=60,
    ha="right",
)

plt.tight_layout()

# Save the second visualization.
plt.savefig(
    chart2_file,
    dpi=150,
)

# Close the graph after saving it.
plt.close()


# ------------------------------------------------------------
# VISUALIZATION 3
# MEDIAN TRANSACTION AMOUNT BY STATUS
# ------------------------------------------------------------

# Create a bar chart comparing median transaction amounts
# for suspicious and non-suspicious transactions.
#
# Each dataset uses its most common currency so that different
# currencies are not mixed together within a dataset.
plt.figure(
    figsize=(10, 6)
)

sns.barplot(
    data=amount_status_summary,
    x="display_source",
    y="median_amount",
    hue="status",
)

plt.title(
    "Median Transaction Amount by Suspicious Status"
)

plt.xlabel(
    "Dataset and Currency"
)

plt.ylabel(
    "Median Transaction Amount"
)

plt.tight_layout()

# Save the third visualization.
plt.savefig(
    chart3_file,
    dpi=150,
)

# Close the graph.
plt.close()


# ------------------------------------------------------------
# AUTOMATIC FINDINGS
# ------------------------------------------------------------

# Create findings using values calculated directly from the data.
finding1 = (
    "The combined analytical dataset contains "
    + f"{num_rows:,}"
    + " transactions and "
    + str(num_columns)
    + " variables."
)

finding2 = (
    "There were "
    + f"{suspicious_count:,}"
    + " suspicious transactions, giving an overall suspicious rate of "
    + f"{overall_suspicious_rate:.4f}%."
)

finding3 = (
    str(highest_source)
    + " had the highest suspicious transaction rate among the datasets at "
    + f"{highest_source_rate:.4f}%."
)

finding4 = (
    "The transaction category with the highest suspicious rate was "
    + str(highest_category)
    + " from "
    + str(highest_category_source)
    + ", with a suspicious rate of "
    + f"{highest_category_rate:.4f}%."
)


# ------------------------------------------------------------
# CREATE THE PDF
# ------------------------------------------------------------

# Create a new PDF report.
pdf = FPDF()

# Automatically start a new page if the current page becomes full.
pdf.set_auto_page_break(
    auto=True,
    margin=15,
)

# Add the first page.
pdf.add_page()


# ------------------------------------------------------------
# PROJECT TITLE
# ------------------------------------------------------------

# Add the project title at the beginning of the PDF.
pdf.set_font(
    "Helvetica",
    "B",
    16,
)

pdf.multi_cell(
    0,
    10,
    "Financial Fraud and Money-Laundering Detection in Transaction Data",
    align="C",
)

pdf.ln(5)


# ------------------------------------------------------------
# DATASET SUMMARY
# ------------------------------------------------------------

# Add the Dataset Summary section heading.
pdf.set_font(
    "Helvetica",
    "B",
    14,
)

pdf.cell(
    0,
    10,
    "1. Dataset Summary",
    ln=True,
)

# Switch to normal text.
pdf.set_font(
    "Helvetica",
    "",
    11,
)

# Add basic dataset information.
pdf.cell(
    0,
    8,
    "Total observations: " + f"{num_rows:,}",
    ln=True,
)

pdf.cell(
    0,
    8,
    "Total variables: " + str(num_columns),
    ln=True,
)

pdf.cell(
    0,
    8,
    "Not suspicious transactions: "
    + f"{not_suspicious_count:,}",
    ln=True,
)

pdf.cell(
    0,
    8,
    "Suspicious transactions: "
    + f"{suspicious_count:,}",
    ln=True,
)

pdf.cell(
    0,
    8,
    "Overall suspicious rate: "
    + f"{overall_suspicious_rate:.4f}%",
    ln=True,
)

pdf.ln(5)


# ------------------------------------------------------------
# RECORD COUNTS BY DATASET
# ------------------------------------------------------------

# Add a small heading for the dataset counts.
pdf.set_font(
    "Helvetica",
    "B",
    11,
)

pdf.cell(
    0,
    8,
    "Records by dataset:",
    ln=True,
)

pdf.set_font(
    "Helvetica",
    "",
    11,
)

# Add one line for each dataset.
for source, count in source_counts.items():

    pdf.cell(
        0,
        8,
        str(source)
        + ": "
        + f"{count:,}",
        ln=True,
    )


# ------------------------------------------------------------
# LABEL TYPES
# ------------------------------------------------------------

pdf.ln(3)

pdf.set_font(
    "Helvetica",
    "B",
    11,
)

pdf.cell(
    0,
    8,
    "Label types:",
    ln=True,
)

pdf.set_font(
    "Helvetica",
    "",
    11,
)

# List how often each type of fraud/laundering label appears.
for label_type, count in label_type_counts.items():

    pdf.cell(
        0,
        8,
        str(label_type)
        + ": "
        + f"{count:,}",
        ln=True,
    )


# ------------------------------------------------------------
# SUMMARY STATISTICS TABLE
# ------------------------------------------------------------

# Start a new page for numerical summary statistics.
pdf.add_page()

pdf.set_font(
    "Helvetica",
    "B",
    14,
)

pdf.cell(
    0,
    10,
    "2. Summary Statistics",
    ln=True,
)

# Explain how currencies were handled.
pdf.set_font(
    "Helvetica",
    "",
    10,
)

pdf.multi_cell(
    0,
    7,
    "Transaction amounts are summarized using the most common currency "
    "within each dataset so that values from different currencies are "
    "not mixed together."
)

pdf.ln(4)


# ------------------------------------------------------------
# TABLE HEADER
# ------------------------------------------------------------

pdf.set_font(
    "Helvetica",
    "B",
    8,
)

pdf.cell(
    32,
    8,
    "Dataset",
    border=1,
)

pdf.cell(
    28,
    8,
    "Currency",
    border=1,
)

pdf.cell(
    25,
    8,
    "Count",
    border=1,
)

pdf.cell(
    28,
    8,
    "Mean",
    border=1,
)

pdf.cell(
    28,
    8,
    "Median",
    border=1,
)

pdf.cell(
    24,
    8,
    "Minimum",
    border=1,
)

pdf.cell(
    25,
    8,
    "Maximum",
    border=1,
    ln=True,
)


# ------------------------------------------------------------
# TABLE VALUES
# ------------------------------------------------------------

pdf.set_font(
    "Helvetica",
    "",
    8,
)

# Add one summary-statistics row for each dataset.
for row in amount_summary.itertuples(index=False):

    pdf.cell(
        32,
        8,
        str(row.dataset_source),
        border=1,
    )

    pdf.cell(
        28,
        8,
        str(row.currency),
        border=1,
    )

    pdf.cell(
        25,
        8,
        f"{row.count:,.0f}",
        border=1,
    )

    pdf.cell(
        28,
        8,
        f"{row.mean:,.2f}",
        border=1,
    )

    pdf.cell(
        28,
        8,
        f"{row.median:,.2f}",
        border=1,
    )

    pdf.cell(
        24,
        8,
        f"{row.minimum:,.2f}",
        border=1,
    )

    pdf.cell(
        25,
        8,
        f"{row.maximum:,.2f}",
        border=1,
        ln=True,
    )


# ------------------------------------------------------------
# VISUALIZATIONS
# ------------------------------------------------------------

# Start a new page for the first visualization.
pdf.add_page()

pdf.set_font(
    "Helvetica",
    "B",
    14,
)

pdf.cell(
    0,
    10,
    "3. Visualizations",
    ln=True,
)

pdf.set_font(
    "Helvetica",
    "B",
    11,
)

pdf.cell(
    0,
    8,
    "Suspicious Transaction Rate by Dataset",
    ln=True,
)

# Insert the first graph.
pdf.image(
    chart1_file,
    x=20,
    w=170,
)


# ------------------------------------------------------------
# SECOND VISUALIZATION
# ------------------------------------------------------------

pdf.add_page()

pdf.set_font(
    "Helvetica",
    "B",
    11,
)

pdf.cell(
    0,
    8,
    "Suspicious Transaction Rate by Category",
    ln=True,
)

# Insert the category graph.
pdf.image(
    chart2_file,
    x=15,
    w=180,
)


# ------------------------------------------------------------
# THIRD VISUALIZATION
# ------------------------------------------------------------

pdf.add_page()

pdf.set_font(
    "Helvetica",
    "B",
    11,
)

pdf.cell(
    0,
    8,
    "Median Transaction Amount by Suspicious Status",
    ln=True,
)

# Insert the median amount graph.
pdf.image(
    chart3_file,
    x=15,
    w=180,
)


# ------------------------------------------------------------
# KEY ANALYTICAL FINDINGS
# ------------------------------------------------------------

# Start a new page for the automatically calculated findings.
pdf.add_page()

pdf.set_font(
    "Helvetica",
    "B",
    14,
)

pdf.cell(
    0,
    10,
    "4. Key Analytical Findings",
    ln=True,
)

pdf.set_font(
    "Helvetica",
    "",
    11,
)

# Add each analytical finding to the report.
pdf.multi_cell(
    0,
    8,
    finding1,
)

pdf.ln(3)

pdf.multi_cell(
    0,
    8,
    finding2,
)

pdf.ln(3)

pdf.multi_cell(
    0,
    8,
    finding3,
)

pdf.ln(3)

pdf.multi_cell(
    0,
    8,
    finding4,
)


# ------------------------------------------------------------
# SAVE THE PDF
# ------------------------------------------------------------

# Save the completed report in the 05-Report folder.
pdf.output(
    report_file
)

# Print a message so the user knows the report was created.
print(
    "PDF report created successfully."
)

print(
    report_file
)
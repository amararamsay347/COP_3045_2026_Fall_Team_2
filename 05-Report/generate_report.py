# Import pandas so the script can read and analyze the CSV dataset.
import pandas as pd

# Import Matplotlib so the script can create and save graphs.
import matplotlib.pyplot as plt

# Import Seaborn to make some of the graphs easier to create.
import seaborn as sns

# Import FPDF so the script can automatically create the PDF report.
from fpdf import FPDF


# ------------------------------------------------------------
# FILE PATHS
# ------------------------------------------------------------

# This is the CSV file that the report will use.
# The filename may need to be changed later depending on what
# your teammate names the final combined analytical dataset.
data_file = "data/combined_analytical_data.csv"

# This is the PDF file that will be created when the script runs.
report_file = "05-Report/project_report.pdf"

# These are the image files that will be created for the graphs.
# The graphs will later be inserted into the PDF.
chart1_file = "05-Report/label_counts.png"
chart2_file = "05-Report/category_counts.png"
chart3_file = "05-Report/hourly_flags.png"


# ------------------------------------------------------------
# READ THE DATASET
# ------------------------------------------------------------

# Read the final analytical CSV into a pandas DataFrame.
df = pd.read_csv(data_file)

# Print a message so the user knows the dataset loaded correctly.
print("Dataset loaded successfully.")


# ------------------------------------------------------------
# DATASET SUMMARY
# ------------------------------------------------------------

# Count the total number of rows in the dataset.
# Each row represents one transaction.
num_rows = df.shape[0]

# Count the total number of columns in the dataset.
num_columns = df.shape[1]

# Count how many transactions came from each original dataset.
# For example, this may show PaySim and IBM AML.
source_counts = df["source"].value_counts()

# Count how many transactions have each label.
# Label 0 represents a normal transaction.
# Label 1 represents a fraud or laundering transaction.
label_counts = df["label"].value_counts()

# Count all transactions that are marked as fraud or laundering.
flagged_count = int((df["label"] == 1).sum())

# Count all transactions that are marked as legitimate.
legitimate_count = int((df["label"] == 0).sum())

# Calculate the percentage of all transactions that were flagged.
flag_rate = flagged_count / num_rows * 100


# ------------------------------------------------------------
# SUMMARY STATISTICS
# ------------------------------------------------------------

# Count how many transaction amount values are available.
amount_count = df["amount"].count()

# Calculate the average transaction amount.
amount_mean = df["amount"].mean()

# Calculate the middle transaction amount.
amount_median = df["amount"].median()

# Calculate the standard deviation of transaction amounts.
# This shows how spread out the transaction amounts are.
amount_std = df["amount"].std()

# Find the smallest transaction amount.
amount_min = df["amount"].min()

# Find the largest transaction amount.
amount_max = df["amount"].max()

# Calculate the average transaction hour.
hour_mean = df["hour"].mean()

# Find the earliest hour in the dataset.
hour_min = df["hour"].min()

# Find the latest hour in the dataset.
hour_max = df["hour"].max()

# Calculate the average transaction amount for legitimate transactions.
legitimate_mean_amount = df[df["label"] == 0]["amount"].mean()

# Calculate the average transaction amount for flagged transactions.
flagged_mean_amount = df[df["label"] == 1]["amount"].mean()


# ------------------------------------------------------------
# CATEGORY ANALYSIS
# ------------------------------------------------------------

# Count how many transactions belong to each transaction category.
# Examples may include PAYMENT, TRANSFER, CASH_OUT, WIRE, or CHEQUE.
category_counts = df["category"].value_counts()

# Calculate the average label for each category.
# Because labels are 0 and 1, the average gives the percentage
# of transactions in that category that were flagged.
category_flag_rates = (
    df.groupby("category")["label"]
    .mean()
    .sort_values(ascending=False)
)

# Find the category with the highest fraud or laundering rate.
highest_flag_category = category_flag_rates.index[0]

# Convert the highest category flag rate into a percentage.
highest_flag_rate = category_flag_rates.iloc[0] * 100


# ------------------------------------------------------------
# VISUALIZATION 1
# LEGITIMATE VS FLAGGED TRANSACTIONS
# ------------------------------------------------------------

# Create a new figure for the first graph.
plt.figure(figsize=(7, 5))

# Create a bar chart showing how many transactions have each label.
sns.countplot(
    data=df,
    x="label"
)

# Add a title and axis labels to make the graph easier to understand.
plt.title("Legitimate vs Flagged Transactions")
plt.xlabel("Transaction Label")
plt.ylabel("Number of Transactions")

# Replace the numbers 0 and 1 with easier-to-read names.
plt.xticks([0, 1], ["Legitimate", "Flagged"])

# Adjust spacing so the graph fits properly.
plt.tight_layout()

# Save the graph as an image so it can be added to the PDF.
plt.savefig(chart1_file)

# Close the graph so it does not stay open in memory.
plt.close()


# ------------------------------------------------------------
# VISUALIZATION 2
# TRANSACTION AND PAYMENT CATEGORIES
# ------------------------------------------------------------

# Create a new figure for the second graph.
plt.figure(figsize=(10, 6))

# Create a bar chart showing the number of transactions
# in each transaction or payment category.
category_counts.plot(kind="bar")

# Add a title and axis labels.
plt.title("Transaction and Payment Categories")
plt.xlabel("Category")
plt.ylabel("Number of Transactions")

# Rotate category names so they do not overlap.
plt.xticks(rotation=45, ha="right")

# Adjust spacing so labels fit inside the graph.
plt.tight_layout()

# Save the second graph as an image.
plt.savefig(chart2_file)

# Close the graph after saving it.
plt.close()


# ------------------------------------------------------------
# VISUALIZATION 3
# FLAGGED TRANSACTIONS BY HOUR
# ------------------------------------------------------------

# Group the dataset by hour and calculate the average label.
# Since the labels are 0 and 1, the average represents the
# percentage of transactions that were flagged during each hour.
hourly_flags = (
    df.groupby("hour")["label"]
    .mean()
    .reset_index()
)

# Convert the decimal flag rate into a percentage.
hourly_flags["flag_rate"] = hourly_flags["label"] * 100

# Create a new figure for the third graph.
plt.figure(figsize=(10, 6))

# Create a line graph showing how the flagged rate changes by hour.
sns.lineplot(
    data=hourly_flags,
    x="hour",
    y="flag_rate",
    marker="o"
)

# Add a title and axis labels.
plt.title("Flagged Transaction Rate by Hour")
plt.xlabel("Hour")
plt.ylabel("Flagged Rate (%)")

# Adjust spacing so the graph displays correctly.
plt.tight_layout()

# Save the third graph as an image.
plt.savefig(chart3_file)

# Close the graph after saving it.
plt.close()


# ------------------------------------------------------------
# CREATE THE PDF REPORT
# ------------------------------------------------------------

# Create a new FPDF object.
# This object will be used to build the entire report.
pdf = FPDF()

# Automatically create a new page when the current page becomes full.
pdf.set_auto_page_break(auto=True, margin=15)

# Add the first page to the PDF.
pdf.add_page()


# ------------------------------------------------------------
# PROJECT TITLE
# ------------------------------------------------------------

# Set the font for the main report title.
pdf.set_font("Arial", "B", 16)

# Add the project title and center it on the page.
pdf.multi_cell(
    0,
    10,
    "Financial Fraud and Money-Laundering Detection in Transaction Data",
    align="C"
)

# Add a small amount of blank space after the title.
pdf.ln(5)


# ------------------------------------------------------------
# DATASET SUMMARY SECTION
# ------------------------------------------------------------

# Add the Dataset Summary section heading.
pdf.set_font("Arial", "B", 14)
pdf.cell(0, 10, "1. Dataset Summary", ln=True)

# Change to a smaller normal font for the summary information.
pdf.set_font("Arial", "", 11)

# Add the total number of observations to the PDF.
pdf.cell(
    0,
    8,
    "Number of observations: " + f"{num_rows:,}",
    ln=True
)

# Add the total number of variables.
pdf.cell(
    0,
    8,
    "Number of variables: " + str(num_columns),
    ln=True
)

# Add the number of legitimate transactions.
pdf.cell(
    0,
    8,
    "Legitimate transactions: " + f"{legitimate_count:,}",
    ln=True
)

# Add the number of flagged transactions.
pdf.cell(
    0,
    8,
    "Flagged transactions: " + f"{flagged_count:,}",
    ln=True
)

# Add the overall fraud or laundering percentage.
pdf.cell(
    0,
    8,
    "Overall flagged rate: " + f"{flag_rate:.4f}%",
    ln=True
)

# Add some spacing before the next part.
pdf.ln(5)

# Add a small heading showing that the next values
# describe how many records came from each dataset.
pdf.set_font("Arial", "B", 11)
pdf.cell(0, 8, "Records by dataset:", ln=True)

# Return to normal text.
pdf.set_font("Arial", "", 11)

# Loop through each dataset source and print its record count.
for source, count in source_counts.items():
    pdf.cell(
        0,
        8,
        str(source) + ": " + f"{count:,}",
        ln=True
    )


# ------------------------------------------------------------
# SUMMARY STATISTICS SECTION
# ------------------------------------------------------------

# Start a new page for the statistics table.
pdf.add_page()

# Add the section heading.
pdf.set_font("Arial", "B", 14)
pdf.cell(0, 10, "2. Summary Statistics", ln=True)

# Create the header row for the statistics table.
pdf.set_font("Arial", "B", 10)

pdf.cell(60, 8, "Statistic", border=1)
pdf.cell(60, 8, "Transaction Amount", border=1)
pdf.cell(60, 8, "Transaction Hour", border=1, ln=True)

# Change back to normal text for the table values.
pdf.set_font("Arial", "", 10)

# Add the number of available observations.
pdf.cell(60, 8, "Count", border=1)
pdf.cell(60, 8, f"{amount_count:,.0f}", border=1)
pdf.cell(60, 8, f"{df['hour'].count():,.0f}", border=1, ln=True)

# Add the mean values.
pdf.cell(60, 8, "Mean", border=1)
pdf.cell(60, 8, f"{amount_mean:,.2f}", border=1)
pdf.cell(60, 8, f"{hour_mean:.2f}", border=1, ln=True)

# Add the minimum values.
pdf.cell(60, 8, "Minimum", border=1)
pdf.cell(60, 8, f"{amount_min:,.2f}", border=1)
pdf.cell(60, 8, f"{hour_min:.0f}", border=1, ln=True)

# Add the maximum values.
pdf.cell(60, 8, "Maximum", border=1)
pdf.cell(60, 8, f"{amount_max:,.2f}", border=1)
pdf.cell(60, 8, f"{hour_max:.0f}", border=1, ln=True)

# Add the median transaction amount.
pdf.cell(60, 8, "Median", border=1)
pdf.cell(60, 8, f"{amount_median:,.2f}", border=1)
pdf.cell(60, 8, "-", border=1, ln=True)

# Add the transaction amount standard deviation.
pdf.cell(60, 8, "Std. Deviation", border=1)
pdf.cell(60, 8, f"{amount_std:,.2f}", border=1)
pdf.cell(60, 8, "-", border=1, ln=True)


# ------------------------------------------------------------
# VISUALIZATIONS SECTION
# ------------------------------------------------------------

# Start a new page for the graphs.
pdf.add_page()

# Add the section heading.
pdf.set_font("Arial", "B", 14)
pdf.cell(0, 10, "3. Visualizations", ln=True)

# Add the title for the first graph.
pdf.set_font("Arial", "B", 11)
pdf.cell(0, 8, "Legitimate vs Flagged Transactions", ln=True)

# Insert the first saved graph into the PDF.
pdf.image(
    chart1_file,
    x=20,
    w=170
)

# Start a new page for the second graph.
pdf.add_page()

# Add the title for the second graph.
pdf.set_font("Arial", "B", 11)
pdf.cell(0, 8, "Transaction and Payment Categories", ln=True)

# Insert the second graph.
pdf.image(
    chart2_file,
    x=15,
    w=180
)

# Start a new page for the third graph.
pdf.add_page()

# Add the title for the third graph.
pdf.set_font("Arial", "B", 11)
pdf.cell(0, 8, "Flagged Transaction Rate by Hour", ln=True)

# Insert the third graph.
pdf.image(
    chart3_file,
    x=15,
    w=180
)


# ------------------------------------------------------------
# KEY ANALYTICAL FINDINGS SECTION
# ------------------------------------------------------------

# Start a new page for the findings.
pdf.add_page()

# Add the section heading.
pdf.set_font("Arial", "B", 14)
pdf.cell(0, 10, "4. Key Analytical Findings", ln=True)

# Change to normal text for the findings.
pdf.set_font("Arial", "", 11)

# Create the first automatically generated finding.
# This reports the overall percentage of transactions that were flagged.
finding1 = (
    "The overall flagged transaction rate was "
    + f"{flag_rate:.4f}%."
)

# Create the second finding.
# This compares average transaction amounts for normal and flagged records.
finding2 = (
    "The average amount for legitimate transactions was "
    + f"{legitimate_mean_amount:,.2f}, compared with "
    + f"{flagged_mean_amount:,.2f} for flagged transactions."
)

# Create the third finding.
# This identifies the transaction category with the highest flagged rate.
finding3 = (
    "The category with the highest flagged transaction rate was "
    + str(highest_flag_category)
    + " at "
    + f"{highest_flag_rate:.4f}%."
)

# Add each finding to the PDF.
pdf.multi_cell(0, 8, finding1)
pdf.ln(3)

pdf.multi_cell(0, 8, finding2)
pdf.ln(3)

pdf.multi_cell(0, 8, finding3)


# ------------------------------------------------------------
# SAVE THE PDF
# ------------------------------------------------------------

# Save the completed report using the report filename created earlier.
pdf.output(report_file)

# Print a confirmation message after the report is created.
print("PDF report created successfully:")
print(report_file)
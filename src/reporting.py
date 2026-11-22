"""Generate charts and a PDF report from the combined transactions."""

from datetime import date

# Import pandas to read and analyze the combined transaction dataset.
import pandas as pd

# Import Matplotlib and Seaborn to create the report visualizations.
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns

# Import FPDF to automatically build the PDF report.
from fpdf import FPDF

from src.data_loading import load_combined_transactions
from src.paths import CLEAN_DATA_FILE, REPORT_FILE
from src.report_statistics import (
    build_findings,
    highlight_categories,
    summarize_amounts,
    summarize_categories,
    summarize_sources,
)

from pathlib import Path


class TransactionReport:
    """Generate charts and a PDF from cleaned transactions."""

    def __init__(self, input_file: Path, output_file: Path) -> None:
        self.input_file = input_file
        self.output_file = output_file
        self.output_dir = output_file.parent

    def _load_transactions(self) -> pd.DataFrame:
        """Load the shared schema and label unspecified currencies for display."""
        df = load_combined_transactions(self.input_file)
        if "N/A" not in df["currency"].cat.categories:
            df["currency"] = df["currency"].cat.add_categories(["N/A"])
        df["currency"] = df["currency"].fillna("N/A")
        return df


    def _plot_suspicious_rate_by_source(
        self, source_summary: pd.DataFrame
    ) -> Path:
        chart_file = self.output_dir / "suspicious_rate_by_source.png"

        plt.figure(figsize=(8, 5))
        sns.barplot(
            data=source_summary,
            x="label_type", order=["fraud", "laundering"],
            y="suspicious_rate",
        )
        plt.title("Suspicious Transaction Rate by Dataset")
        plt.xlabel("Positive label (PaySim fraud / IBM laundering)")
        plt.ylabel("Suspicious Rate (%)")
        plt.tight_layout()
        plt.savefig(chart_file, dpi=150)
        plt.close()

        return chart_file

    def _plot_suspicious_rate_by_category(
        self, category_summary: pd.DataFrame
    ) -> Path:
        chart_file = self.output_dir / "suspicious_rate_by_category.png"

        plt.figure(figsize=(12, 7))
        sns.barplot(
            data=category_summary,
            x="display_category",
            y="suspicious_rate",
        )
        plt.title("Suspicious Transaction Rate by Category")
        plt.xlabel("Dataset and Transaction Category")
        plt.ylabel("Suspicious Rate (%)")
        plt.xticks(rotation=60, ha="right")
        plt.tight_layout()
        plt.savefig(chart_file, dpi=150)
        plt.close()

        return chart_file

    def _plot_median_amount_by_status(
        self, amount_status_summary: pd.DataFrame
    ) -> Path:
        chart_file = self.output_dir / "median_amount_by_status.png"

        plt.figure(figsize=(10, 6))
        sns.barplot(
            data=amount_status_summary,
            x="display_source",
            y="median_amount",
            hue="status",
        )
        plt.title("Median Transaction Amount by Suspicious Status")
        plt.xlabel("Dataset and Currency")
        plt.ylabel("Median Transaction Amount (log scale)")
        plt.yscale("log")
        plt.tight_layout()
        plt.savefig(chart_file, dpi=150)
        plt.close()

        return chart_file

    def _add_dataset_overview(
        self, pdf: FPDF, num_rows: int, num_columns: int,
        source_summary: pd.DataFrame,
    ) -> None:
        source_counts = source_summary.set_index("dataset_source")["transaction_count"]
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
            new_x="LMARGIN",
        )

        pdf.set_font(
            "Helvetica",
            "",
            10,
        )

        pdf.multi_cell(
            0,
            7,
            f"COP 3045 Python Programming II - Team 2 | {date.today():%B %d, %Y}",
            align="C",
            new_x="LMARGIN",
        )

        pdf.multi_cell(
            0,
            6,
            "PaySim "
            + f"({source_counts.get('PAYSim', 0):,} mobile-money transactions) "
            + "and IBM AML HI-Small "
            + f"({source_counts.get('IBM', 0):,} bank transactions), both synthetic.",
            align="C",
            new_x="LMARGIN",
        )

        pdf.ln(4)


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
            "Total variables: " + str(num_columns) + " (union of both datasets' columns)",
            ln=True,
        )

        pdf.ln(5)
        for row in source_summary.itertuples(index=False):
            pdf.multi_cell(
                0,
                8,
                f"{row.dataset_source} {row.label_type} labels: "
                f"{row.suspicious_count:,} of {row.transaction_count:,} "
                f"({row.suspicious_rate:.4f}%).",
                new_x="LMARGIN",
            )


    def _add_statistics_tables(
        self, pdf: FPDF, amount_summary: pd.DataFrame, category_summary: pd.DataFrame
    ) -> None:
        ibm_amounts = amount_summary.loc[
            amount_summary["dataset_source"] == "IBM",
            "maximum",
        ]

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
            "not mixed together. PaySim amounts are reported in simulation units.",
            new_x="LMARGIN",
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


        pdf.ln(5)
        pdf.set_font(
            "Helvetica",
            "B",
            10,
        )
        pdf.cell(
            0,
            8,
            "Spread and quartiles:",
            ln=True,
        )

        pdf.set_font(
            "Helvetica",
            "B",
            8,
        )
        for width, title in (
            (35, "Dataset"),
            (32, "Currency"),
            (40, "Std. Dev."),
            (40, "25th Percentile"),
            (40, "75th Percentile"),
        ):
            pdf.cell(width, 8, title, border=1)
        pdf.ln()

        pdf.set_font(
            "Helvetica",
            "",
            8,
        )
        for row in amount_summary.itertuples(index=False):
            for width, value in (
                (35, str(row.dataset_source)),
                (32, str(row.currency)),
                (40, f"{row.std:,.2f}"),
                (40, f"{row.percentile_25:,.2f}"),
                (40, f"{row.percentile_75:,.2f}"),
            ):
                pdf.cell(width, 8, value, border=1)
            pdf.ln()

        if not ibm_amounts.empty:
            pdf.ln(3)
            pdf.set_font(
                "Helvetica",
                "",
                9,
            )
            pdf.multi_cell(
                0,
                6,
                "The IBM maximum of "
                + f"{ibm_amounts.iloc[0]:,.2f} is an extreme outlier, so the median is the "
                "more reliable measure of a typical transaction.",
                new_x="LMARGIN",
            )

        pdf.ln(4)
        pdf.set_font(
            "Helvetica",
            "B",
            10,
        )
        pdf.cell(
            0,
            8,
            "Category highlights by dataset",
            ln=True,
        )

        pdf.set_font(
            "Helvetica",
            "",
            8,
        )
        pdf.multi_cell(
            0,
            6,
            "Each source shows its highest label rates and the category with the most flagged transactions.",
            new_x="LMARGIN",
        )

        pdf.set_font(
            "Helvetica",
            "B",
            8,
        )
        for width, title in (
            (82, "Dataset and category"),
            (35, "Transactions"),
            (35, "Flagged"),
            (35, "Label rate"),
        ):
            pdf.cell(width, 8, title, border=1)
        pdf.ln()

        pdf.set_font(
            "Helvetica",
            "",
            8,
        )
        for row in highlight_categories(category_summary).itertuples(index=False):
            pdf.cell(82, 8, row.display_category, border=1)
            pdf.cell(35, 8, f"{row.transaction_count:,}", border=1)
            pdf.cell(35, 8, f"{row.suspicious_count:,}", border=1)
            pdf.cell(35, 8, f"{row.suspicious_rate:.4f}%", border=1)
            pdf.ln()

    def _add_chart_pages(
        self, pdf: FPDF, chart1_file: Path, chart2_file: Path, chart3_file: Path
    ) -> None:
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

        pdf.set_x(pdf.l_margin)
        pdf.set_font("Helvetica", "", 9)
        pdf.multi_cell(0, 6, "Suspicious rates are shown separately for PaySim fraud and IBM laundering labels. Interpret each rate relative to its dataset.", new_x="LMARGIN")


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

        pdf.set_x(pdf.l_margin)
        pdf.set_font("Helvetica", "", 9)
        pdf.multi_cell(0, 6, "Categories are ordered by positive-label rate within each dataset. Read each rate alongside its transaction count.", new_x="LMARGIN")


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

        pdf.set_x(pdf.l_margin)
        pdf.set_font("Helvetica", "", 9)
        pdf.multi_cell(0, 6, "The logarithmic vertical axis keeps the PaySim and IBM medians readable on the same chart.", new_x="LMARGIN")

    def _add_findings_page(self, pdf: FPDF, findings: list[str]) -> None:
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
        for finding in findings:
            pdf.multi_cell(0, 8, finding, new_x="LMARGIN")
            pdf.ln(3)

    def generate(self) -> None:
        """Analyze the cleaned transactions and write the charts and PDF."""
        self.output_dir.mkdir(parents=True, exist_ok=True)

        df = self._load_transactions()

        # ------------------------------------------------------------
        # BASIC DATASET INFORMATION
        # ------------------------------------------------------------

        # Count the total number of transactions.
        num_rows = len(df)

        # Count the total number of variables used in the analytical dataset.
        num_columns = len(pd.read_csv(self.input_file, nrows=0).columns)

        source_summary = summarize_sources(df)
        category_summary = summarize_categories(df)
        amount_summary, amount_status_summary = summarize_amounts(df)


        chart1_file = self._plot_suspicious_rate_by_source(source_summary)
        chart2_file = self._plot_suspicious_rate_by_category(category_summary)
        chart3_file = self._plot_median_amount_by_status(amount_status_summary)
        findings = build_findings(num_rows, source_summary, category_summary, amount_status_summary)

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

        self._add_dataset_overview(pdf, num_rows, num_columns, source_summary)
        self._add_statistics_tables(pdf, amount_summary, category_summary)
        self._add_chart_pages(pdf, chart1_file, chart2_file, chart3_file)
        self._add_findings_page(pdf, findings)

        # ------------------------------------------------------------
        # SAVE THE PDF
        # ------------------------------------------------------------

        # Save the completed report in the 05-Report folder.
        pdf.output(
            self.output_file
        )

        # Print a message so the user knows the report was created.
        print(
            "PDF report created successfully."
        )

        print(
            self.output_file
        )


def main() -> None:
    report = TransactionReport(CLEAN_DATA_FILE, REPORT_FILE)
    report.generate()

if __name__ == "__main__":
    main()

"""PDF report construction."""

from datetime import datetime, timezone
from pathlib import Path
import pandas as pd
from fpdf import FPDF

from .analysis import ReportMetrics


class PDFReport:
    """Build a formatted PDF report from loaded transaction metrics."""

    def __init__(self, title: str = "Financial Fraud and Money-Laundering Detection") -> None:
        self._title = title
        self._pdf = FPDF()
        self._pdf.set_creation_date(
            datetime(2000, 1, 1, tzinfo=timezone.utc)
        )
        self._pdf.set_auto_page_break(auto=True, margin=15)

    def build(
        self,
        frame: pd.DataFrame,
        total_columns: int,
        metrics: ReportMetrics,
        chart_files: dict[str, Path],
        output_file: Path,
    ) -> Path:
        """Write all report sections and charts to a PDF file."""
        output_file = Path(output_file)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        pdf = self._pdf
        pdf.add_page()

        pdf.set_font("Helvetica", "B", 16)
        pdf.multi_cell(0, 10, self._title, align="C")
        pdf.set_font("Helvetica", "", 10)
        pdf.set_x(pdf.l_margin)
        pdf.multi_cell(0, 6, "Automated transaction analysis report", align="C")
        pdf.set_x(pdf.l_margin)
        pdf.multi_cell(
            0,
            6,
            "Automated analysis of the combined transaction dataset.",
            align="C",
        )

        num_rows = len(frame)
        not_suspicious = int((frame["is_suspicious"] == 0).sum())
        suspicious = int((frame["is_suspicious"] == 1).sum())
        overall_rate = suspicious / num_rows * 100 if num_rows else 0.0

        pdf.ln(5)
        pdf.set_font("Helvetica", "B", 14)
        pdf.cell(0, 10, "1. Dataset Summary", ln=True)
        pdf.set_font("Helvetica", "", 11)
        for text in (
            f"Total observations: {num_rows:,}",
            f"Total variables: {total_columns}",
            f"Not suspicious transactions: {not_suspicious:,}",
            f"Suspicious transactions: {suspicious:,}",
            f"Overall suspicious rate: {overall_rate:.4f}%",
        ):
            pdf.cell(0, 8, text, ln=True)

        pdf.ln(3)
        pdf.set_font("Helvetica", "B", 11)
        pdf.cell(0, 8, "Records by dataset:", ln=True)
        pdf.set_font("Helvetica", "", 11)
        for source, count in frame["dataset_source"].value_counts().items():
            pdf.cell(0, 8, f"{source}: {count:,}", ln=True)

        pdf.ln(3)
        pdf.set_font("Helvetica", "B", 11)
        pdf.cell(0, 8, "Label types:", ln=True)
        pdf.set_font("Helvetica", "", 11)
        for label, count in frame["label_type"].value_counts().items():
            pdf.cell(0, 8, f"{label}: {count:,}", ln=True)

        pdf.add_page()
        pdf.set_font("Helvetica", "B", 14)
        pdf.cell(0, 10, "2. Summary Statistics", ln=True)
        pdf.set_font("Helvetica", "", 10)
        pdf.multi_cell(
            0,
            7,
            "Amount summaries use the most common currency within each dataset "
            "source; values across different currencies are not combined.",
        )

        pdf.ln(4)
        self._amount_table(metrics.amount_summary)
        pdf.ln(4)
        pdf.set_font("Helvetica", "B", 10)
        pdf.cell(0, 8, "Spread and quartiles:", ln=True)
        pdf.set_font("Helvetica", "B", 8)
        quartile_columns = (
            (35, "Dataset"),
            (32, "Currency"),
            (40, "Std. Dev."),
            (40, "25th Percentile"),
            (40, "75th Percentile"),
        )
        for width, title in quartile_columns:
            pdf.cell(width, 8, title, border=1)
        pdf.ln()
        pdf.set_font("Helvetica", "", 8)
        for row in metrics.amount_summary.itertuples(index=False):
            for width, value in zip(
                (35, 32, 40, 40, 40),
                (
                    str(row.dataset_source),
                    str(row.currency),
                    f"{row.std:,.2f}",
                    f"{row.percentile_25:,.2f}",
                    f"{row.percentile_75:,.2f}",
                ),
            ):
                pdf.cell(width, 8, value, border=1)
            pdf.ln()

        if not metrics.amount_summary.empty:
            pdf.ln(3)
            pdf.set_font("Helvetica", "", 9)
            pdf.multi_cell(
                0,
                6,
                "Maximum values can be affected by unusually large transactions; "
                "compare them with the median when describing a typical amount.",
            )

        pdf.ln(3)
        pdf.set_font("Helvetica", "B", 10)
        pdf.cell(0, 8, "Categorical summary (top 8 categories by suspicious rate):", ln=True)
        pdf.set_font("Helvetica", "", 9)
        pdf.multi_cell(
            0,
            6,
            "Counts provide context for each rate; categories with few "
            "transactions can have volatile rates.",
        )
        pdf.set_font("Helvetica", "B", 8)
        for width, title in ((88, "Dataset and category"), (42, "Transactions"), (42, "Suspicious rate")):
            pdf.cell(width, 8, title, border=1)
        pdf.ln()
        pdf.set_font("Helvetica", "", 8)
        for row in metrics.category_summary.head(8).itertuples(index=False):
            pdf.cell(88, 8, str(row.display_category), border=1)
            pdf.cell(42, 8, f"{row.transaction_count:,}", border=1)
            pdf.cell(42, 8, f"{row.suspicious_rate:.4f}%", border=1)
            pdf.ln()

        pdf.add_page()
        pdf.set_font("Helvetica", "B", 14)
        pdf.cell(0, 10, "3. Visualizations", ln=True)
        self._chart_page(
            pdf,
            "Suspicious Transaction Rate by Dataset",
            chart_files["source"],
            "Rates are shown by dataset source; interpret them in the context "
            "of each source's label definition.",
        )

        pdf.add_page()
        self._chart_page(pdf, "Suspicious Transaction Rate by Category", chart_files["category"], "Category rates should be read alongside transaction counts.")
        pdf.add_page()
        self._chart_page(
            pdf,
            "Median Transaction Amount by Suspicious Status",
            chart_files["status"],
            "Each source uses its most common currency. The logarithmic scale "
            "supports comparison when amount ranges differ.",
        )

        pdf.set_font("Helvetica", "B", 14)
        pdf.cell(0, 10, "4. Key Analytical Findings", ln=True)
        pdf.set_font("Helvetica", "", 11)
        for finding in self._findings(frame, total_columns, metrics):
            pdf.multi_cell(0, 7, finding)
            pdf.ln(2)

        pdf.output(str(output_file))
        return output_file

    def _amount_table(self, amount_summary: pd.DataFrame) -> None:
        pdf = self._pdf
        pdf.set_font("Helvetica", "B", 8)
        for width, title in ((32, "Dataset"), (28, "Currency"), (25, "Count"), (28, "Mean"), (28, "Median"), (24, "Minimum"), (25, "Maximum")):
            pdf.cell(width, 8, title, border=1)
        pdf.ln()
        pdf.set_font("Helvetica", "", 8)
        for row in amount_summary.itertuples(index=False):
            values = (str(row.dataset_source), str(row.currency), f"{row.count:,.0f}", f"{row.mean:,.2f}", f"{row.median:,.2f}", f"{row.minimum:,.2f}", f"{row.maximum:,.2f}")
            for width, value in zip((32, 28, 25, 28, 28, 24, 25), values):
                pdf.cell(width, 8, value, border=1)
            pdf.ln()

    def _chart_page(self, pdf: FPDF, title: str, chart_file: Path, caption: str) -> None:
        pdf.set_font("Helvetica", "B", 11)
        pdf.cell(0, 8, title, ln=True)
        pdf.image(str(chart_file), x=15, w=170)
        pdf.set_font("Helvetica", "", 9)
        pdf.multi_cell(0, 6, caption)

    def _findings(
        self,
        frame: pd.DataFrame,
        total_columns: int,
        metrics: ReportMetrics,
    ) -> list[str]:
        num_rows = len(frame)
        suspicious = int(frame["is_suspicious"].sum())
        overall_rate = suspicious / num_rows * 100 if num_rows else 0.0
        highest_source = metrics.source_summary.loc[metrics.source_summary["suspicious_rate"].idxmax()]
        highest_category = metrics.category_summary.iloc[0]
        findings = [
            f"The combined analytical dataset contains {num_rows:,} transactions and {total_columns} variables.",
            f"There were {suspicious:,} suspicious transactions, giving an overall suspicious rate of {overall_rate:.4f}%.",
            f"{highest_source['dataset_source']} had the highest dataset suspicious rate at {highest_source['suspicious_rate']:.4f}%.",
            f"The highest-risk category was {highest_category['display_category']} at {highest_category['suspicious_rate']:.4f}%.",
        ]
        for source, group in metrics.amount_status_summary.groupby("display_source"):
            medians = group.set_index("status")["median_amount"]
            if {"Suspicious", "Not Suspicious"}.issubset(medians.index):
                suspicious_median = medians["Suspicious"]
                non_suspicious_median = medians["Not Suspicious"]
                if pd.notna(suspicious_median) and pd.notna(non_suspicious_median):
                    if non_suspicious_median > 0:
                        findings.append(
                            f"In {source}, the median suspicious transaction "
                            f"({suspicious_median:,.2f}) was "
                            f"{suspicious_median / non_suspicious_median:.1f}x "
                            "the median non-suspicious one "
                            f"({non_suspicious_median:,.2f})."
                        )

        top_categories = metrics.category_summary.head(3)["display_category"].tolist()
        findings.append("The three highest-risk categories were " + ", ".join(top_categories) + ".")
        findings.append(
            "Limitation: suspicious rates depend on the dataset composition and "
            "should not be interpreted as real-world prevalence estimates."
        )
        return findings

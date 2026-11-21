"""Small integration tests for the reporting package."""

from pathlib import Path
from tempfile import TemporaryDirectory
import pandas as pd

from src.reporting.loader import load_combined_data
from src.reporting.application import ReportApplication
from src.reporting.analysis import build_metrics
from src.reporting.pdf_report import PDFReport


def test_loader_and_report() -> None:
    with TemporaryDirectory() as directory:
        root = Path(directory)
        data_file = root / "combined.csv"
        pd.DataFrame({
            "transaction_amount": [10.0, 20.0],
            "currency": [None, "USD"],
            "transaction_category": ["PAYMENT", "ACH"],
            "dataset_source": ["PAYSim", "IBM"],
            "label_type": ["fraud", "laundering"],
            "is_suspicious": [0, 1],
            "additional_dataset_field": ["first", "second"],
        }).to_csv(data_file, index=False)

        frame, total_columns = load_combined_data(data_file)
        assert len(frame) == 2
        assert total_columns == 7
        metrics = build_metrics(frame)
        findings = PDFReport()._findings(frame, total_columns, metrics)
        assert "7 variables" in findings[0]
        assert "1 suspicious transactions" in findings[1]
        assert "50.0000%" in findings[1]
        assert metrics.source_summary.loc[
            metrics.source_summary["dataset_source"] == "IBM",
            "suspicious_rate",
        ].iloc[0] == 100
        assert metrics.category_summary.iloc[0]["display_category"] == "IBM - ACH"
        assert metrics.category_summary.iloc[0]["transaction_count"] == 1

        output = ReportApplication(data_file, root / "report").run()
        assert output.is_file()
        repeated_output = ReportApplication(
            data_file, root / "repeated-report"
        ).run()
        assert output.read_bytes() == repeated_output.read_bytes()
        for chart_name in (
            "suspicious_rate_by_source.png",
            "suspicious_rate_by_category.png",
            "median_amount_by_status.png",
        ):
            assert (
                (root / "report" / chart_name).read_bytes()
                == (root / "repeated-report" / chart_name).read_bytes()
            )

        invalid_data_file = root / "missing_label.csv"
        pd.DataFrame({
            "transaction_amount": [10.0],
            "currency": ["USD"],
            "transaction_category": ["PAYMENT"],
            "dataset_source": ["Example"],
            "label_type": ["fraud"],
            "is_suspicious": [None],
        }).to_csv(invalid_data_file, index=False)
        try:
            load_combined_data(invalid_data_file)
        except ValueError as error:
            assert "is_suspicious contains missing" in str(error)
        else:
            raise AssertionError("Missing suspicious labels must not be accepted.")


if __name__ == "__main__":
    test_loader_and_report()
    print("Reporting test passed.")

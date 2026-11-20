"""Small integration tests for the reporting package."""

from pathlib import Path
from tempfile import TemporaryDirectory
import pandas as pd

from src.reporting.loader import load_combined_data
from src.reporting.application import ReportApplication


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
        }).to_csv(data_file, index=False)

        frame, total_columns = load_combined_data(data_file)
        assert len(frame) == 2
        assert total_columns == 6

        output = ReportApplication(data_file, root / "report").run()
        assert output.is_file()


if __name__ == "__main__":
    test_loader_and_report()
    print("Reporting test passed.")

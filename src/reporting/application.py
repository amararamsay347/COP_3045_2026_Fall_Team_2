"""Application orchestration for the reporting package."""

from pathlib import Path
import pandas as pd

from .loader import load_combined_data
from .analysis import build_metrics, ReportMetrics
from .charts import save_charts
from .pdf_report import PDFReport


class ReportApplication:
    """Central reporting workflow that loads data, analyzes it, and builds a PDF."""

    def __init__(
        self,
        data_file: Path,
        output_dir: Path,
        report_name: str = "project_report.pdf",
    ) -> None:
        self._data_file = Path(data_file)
        self._output_dir = Path(output_dir)
        self._output_dir.mkdir(parents=True, exist_ok=True)
        self._report_file = self._output_dir / report_name

        self._frame: pd.DataFrame | None = None
        self._total_columns = 0
        self._metrics: ReportMetrics | None = None

    def load(self) -> None:
        """Load and validate the combined dataset."""
        self._frame, self._total_columns = load_combined_data(self._data_file)

    def analyze(self) -> ReportMetrics:
        """Validate loaded data and calculate reusable report metrics."""
        if self._frame is None:
            raise RuntimeError("Call load() before analyze().")
        self._metrics = build_metrics(self._frame)
        return self._metrics

    def generate(self) -> Path:
        """Generate charts and the PDF report, returning the PDF path."""
        if self._frame is None:
            self.load()
        if self._metrics is None:
            self.analyze()

        chart_files = save_charts(self._metrics, self._output_dir)
        report = PDFReport()
        report.build(
            self._frame,
            self._total_columns,
            self._metrics,
            chart_files,
            self._report_file,
        )
        print(f"PDF report created successfully: {self._report_file}")
        return self._report_file

    def run(self) -> Path:
        """Run the complete reporting workflow."""
        self.load()
        self.analyze()
        return self.generate()

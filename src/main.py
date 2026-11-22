from pathlib import Path
import sys
from collections.abc import Callable

# Allow the project package to be imported when this script is run directly.
if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.data_loading import find_dataset
from src.data_processing import TransactionDataProcessor, inspect_paysim
from src.eda import main as run_eda
from src.paths import (
    CLEAN_DATA_FILE,
    IBM_CLEANED_FILE,
    IBM_FILE,
    LOCAL_IBM_FILE,
    LOCAL_PAYSIM_FILE,
    PAYSIM_CLEANED_FILE,
    PAYSIM_FILE,
    PROCESSED_DIR,
    PROJECT_DIR,
    REPORT_FILE,
)
from src.reporting import main as generate_report
from src.summary_statistics import main as summarize_transactions


def _print_section(heading: str, value: object) -> None:
    """Print a named result from the cleaning stage."""
    print(f"\n{heading}:")
    print(value)


def prepare_transactions() -> None:
    """Clean both datasets and export the source and combined files."""

    paysim_file = find_dataset(PAYSIM_FILE, LOCAL_PAYSIM_FILE)
    ibm_file = find_dataset(IBM_FILE, LOCAL_IBM_FILE)

    processor = TransactionDataProcessor(
        paysim_path=paysim_file,
        ibm_path=ibm_file
    )

    # Preview the raw PaySim sample before cleaning the full datasets.
    inspect_paysim(paysim_file)

    print("\n" + "=" * 50 + "\n")

    # Clean both datasets using the TransactionDataProcessor class.
    processor.clean_data()

    # Retrieve the cleaned DataFrames for reporting and CSV exports.
    paysim, ibm = processor.get_cleaned_data()

    # Save cleaned datasets so the summary-statistics script can analyze these outputs.
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    paysim_output = PAYSIM_CLEANED_FILE
    ibm_output = IBM_CLEANED_FILE
    paysim.to_csv(paysim_output, index=False)
    ibm.to_csv(ibm_output, index=False)

    for dataset_name, transactions in (("PaySim", paysim), ("IBM", ibm)):
        _print_section(f"{dataset_name} cleaned data head", transactions.head())
        _print_section(f"{dataset_name} cleaned data shape", transactions.shape)

    _print_section("PaySim fraud labels", paysim["isFraud"].value_counts())
    _print_section("IBM laundering labels", ibm["Is Laundering"].value_counts())
    _print_section("PaySim transaction types", paysim["type"].value_counts())
    _print_section("IBM payment formats", ibm["Payment Format"].value_counts())
    _print_section("PaySim hours", paysim["hour"].describe())
    _print_section("IBM hours", ibm["hour"].describe())

    print(f"\nCleaned PaySim dataset saved to: {paysim_output}")
    print(f"Cleaned IBM dataset saved to: {ibm_output}")

    # Export the combined cleaned data required by the graphical EDA assignment.
    combined_transactions = processor.combine_data()
    CLEAN_DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    combined_transactions.to_csv(CLEAN_DATA_FILE, index=False, chunksize=100_000)
    print(f"\nCombined cleaned dataset saved to: {CLEAN_DATA_FILE}")


def _run_stage(
    name: str, operation: Callable[[], None], recovery: str
) -> None:
    """Run one pipeline stage and report expected failures to the caller."""
    print(f"=== {name} ===", flush=True)
    try:
        operation()
    except (OSError, ValueError) as error:
        raise SystemExit(f"{name} failed: {error}\n{recovery}") from None


def main() -> None:
    """Run data preparation, summary statistics, EDA, and PDF reporting."""
    _run_stage(
        "Data preparation",
        prepare_transactions,
        f"Check the raw CSV inputs for PaySim ({PAYSIM_FILE}) and IBM ({IBM_FILE}).",
    )
    _run_stage(
        "Summary statistics",
        summarize_transactions,
        f"Check the cleaned CSVs in {PROCESSED_DIR} and rerun the workflow.",
    )
    _run_stage(
        "Exploratory data analysis",
        run_eda,
        f"Check {CLEAN_DATA_FILE} and that the chart directory is writable.",
    )
    _run_stage(
        "PDF reporting",
        generate_report,
        f"Check {CLEAN_DATA_FILE} and that {REPORT_FILE} is writable.",
    )
    print(f"Done. Report: {REPORT_FILE.relative_to(PROJECT_DIR).as_posix()}")


if __name__ == "__main__":
    main()

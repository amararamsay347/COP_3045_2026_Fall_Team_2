"""Project-relative paths shared by all pipeline stages."""

from pathlib import Path


PROJECT_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_DIR / "data"
PAYSIM_FILE = DATA_DIR / "paysim_data.csv"
IBM_FILE = DATA_DIR / "HI-Small_Trans.csv"
LOCAL_PAYSIM_FILE = DATA_DIR / "ibm" / PAYSIM_FILE.name
LOCAL_IBM_FILE = DATA_DIR / "IBM_small_HI_data" / IBM_FILE.name

PROCESSED_DIR = DATA_DIR / "processed"
PAYSIM_CLEANED_FILE = PROCESSED_DIR / "paysim_cleaned.csv"
IBM_CLEANED_FILE = PROCESSED_DIR / "ibm_cleaned.csv"
CLEAN_DATA_FILE = PROJECT_DIR / "03-Data cleaning" / "clean_data.csv"

EDA_OUTPUT_DIR = PROJECT_DIR / "04-EDA" / "output"
IBM_METADATA_DIR = DATA_DIR / "ibm" / "IBM_small_HI_data"
IBM_ACCOUNTS_FILE = IBM_METADATA_DIR / "HI-Small_accounts.csv"
IBM_PATTERNS_FILE = IBM_METADATA_DIR / "HI-Small_Patterns.csv"

REPORT_DIR = PROJECT_DIR / "05-Report"
REPORT_FILE = REPORT_DIR / "project_report.pdf"

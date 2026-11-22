"""Chart generation for the automated report."""

from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns

from .analysis import ReportMetrics


def save_charts(metrics: ReportMetrics, output_dir: Path) -> dict[str, Path]:
    """Create and save all report charts."""
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    source_file = output_dir / "suspicious_rate_by_source.png"
    plt.figure(figsize=(8, 5))
    sns.barplot(data=metrics.source_summary, x="dataset_source", y="suspicious_rate")
    plt.title("Suspicious Transaction Rate by Dataset")
    plt.xlabel("Dataset")
    plt.ylabel("Suspicious Rate (%)")
    plt.tight_layout()
    plt.savefig(source_file, dpi=150)
    plt.close()

    category_file = output_dir / "suspicious_rate_by_category.png"
    plt.figure(figsize=(12, 7))
    sns.barplot(data=metrics.category_summary, x="display_category", y="suspicious_rate")
    plt.title("Suspicious Transaction Rate by Category")
    plt.xlabel("Dataset and Transaction Category")
    plt.ylabel("Suspicious Rate (%)")
    plt.xticks(rotation=60, ha="right")
    plt.tight_layout()
    plt.savefig(category_file, dpi=150)
    plt.close()

    status_file = output_dir / "median_amount_by_status.png"
    plt.figure(figsize=(10, 6))
    sns.barplot(
        data=metrics.amount_status_summary,
        x="display_source",
        y="median_amount",
        hue="status",
    )
    plt.title("Median Transaction Amount by Suspicious Status")
    plt.xlabel("Dataset and Currency")
    plt.ylabel("Median Transaction Amount (log scale)")
    plt.yscale("log")
    plt.tight_layout()
    plt.savefig(status_file, dpi=150)
    plt.close()

    return {
        "source": source_file,
        "category": category_file,
        "status": status_file,
    }

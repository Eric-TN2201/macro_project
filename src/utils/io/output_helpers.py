# Student Name:
# +  u3281913
# +   u3293786
# Unit: Software Technology 1 (8995)
# Assignment: Assignment 3 - Macroinvertebrate Image Analysis System

from pathlib import Path


def filter_existing_options(options: dict[str, tuple[Path, str]]) -> dict[str, tuple[Path, str]]:
    """Return only output options whose target files currently exist."""
    return {name: option for name, option in options.items() if option[0].exists()}


def read_text_or_default(path: Path, default: str = "") -> str:
    """Read UTF-8 text from a file, returning a default string when missing."""
    return path.read_text(encoding="utf-8") if path.exists() else default


def build_report_options(report_output_dir: Path) -> dict[str, tuple[Path, str]]:
    """Build report output option mapping for the report selector."""
    return {
        "Classification Report": (report_output_dir / "classification_report.txt", "text"),
        "Confusion Report": (report_output_dir / "confusion_matrix.png", "image"),
    }


def build_eda_options(eda_output_dir: Path) -> dict[str, tuple[Path, str]]:
    """Build EDA output option mapping for the EDA selector."""
    return {
        "Dataset Summary (CSV)": (eda_output_dir / "dataset_summary.csv", "csv"),
        "Class Counts (CSV)": (eda_output_dir / "class_counts.csv", "csv"),
        "Class Distribution": (eda_output_dir / "class_distribution.png", "image"),
        "Image Size Distribution": (eda_output_dir / "image_size_distribution.png", "image"),
        "Sample Grid": (eda_output_dir / "sample_grid.png", "image"),
    }

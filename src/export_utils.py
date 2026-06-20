"""Export helpers for analysis tables."""

from __future__ import annotations

from io import BytesIO
from zipfile import ZIP_DEFLATED, ZipFile

import pandas as pd

from src.io_utils import dataframe_to_csv_bytes


def make_csv_download(df: pd.DataFrame) -> bytes:
    """Return CSV bytes for a Streamlit download button."""

    return dataframe_to_csv_bytes(df)


def build_export_tables(
    cleaned_dataset: pd.DataFrame,
    enrollment_year: pd.DataFrame,
    enrollment_course: pd.DataFrame,
    matrix: pd.DataFrame,
    missing_report: pd.DataFrame,
    age_report: pd.DataFrame | None = None,
    categorical_report: pd.DataFrame | None = None,
) -> dict[str, pd.DataFrame]:
    """Collect exportable analysis tables in a predictable structure."""

    tables = {
        "cleaned_dataset.csv": cleaned_dataset,
        "enrollment_by_year.csv": enrollment_year,
        "enrollment_by_course.csv": enrollment_course,
        "year_course_matrix.csv": matrix.reset_index() if not matrix.empty else matrix,
        "missing_values_report.csv": missing_report,
    }
    if age_report is not None and not age_report.empty:
        tables["age_summary.csv"] = age_report
    if categorical_report is not None and not categorical_report.empty:
        tables["categorical_summary.csv"] = categorical_report
    return tables


def build_zip_export(tables: dict[str, pd.DataFrame]) -> bytes:
    """Build a ZIP archive containing CSV exports."""

    buffer = BytesIO()
    with ZipFile(buffer, mode="w", compression=ZIP_DEFLATED) as archive:
        for filename, table in tables.items():
            archive.writestr(filename, make_csv_download(table))
    return buffer.getvalue()

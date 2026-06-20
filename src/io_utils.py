"""Input/output helpers for uploaded files and CSV exports."""

from __future__ import annotations

from io import BytesIO
from pathlib import Path
from typing import Iterable

import pandas as pd


def load_csv(file_or_path) -> pd.DataFrame:
    """Load a CSV file from a path or in-memory upload."""

    return pd.read_csv(file_or_path)


def read_excel_sheets(file_or_path) -> list[str]:
    """Return sheet names from an Excel file."""

    excel = pd.ExcelFile(file_or_path)
    return list(excel.sheet_names)


def load_excel(file_or_path, sheet_name: str | None = None, read_all_sheets: bool = False) -> pd.DataFrame:
    """Load one Excel sheet or combine all sheets into one DataFrame."""

    if read_all_sheets:
        sheets = pd.read_excel(file_or_path, sheet_name=None)
        frames: list[pd.DataFrame] = []
        for sheet, frame in sheets.items():
            frame = frame.copy()
            frame["source_sheet"] = sheet
            frames.append(frame)
        return pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()

    return pd.read_excel(file_or_path, sheet_name=sheet_name or 0)


def _load_single_file(uploaded_file, read_all_sheets: bool = True, selected_sheet: str | None = None) -> pd.DataFrame:
    file_name = getattr(uploaded_file, "name", str(uploaded_file))
    suffix = Path(file_name).suffix.lower()

    if suffix == ".csv":
        frame = load_csv(uploaded_file)
    elif suffix in {".xls", ".xlsx"}:
        frame = load_excel(uploaded_file, sheet_name=selected_sheet, read_all_sheets=read_all_sheets)
    else:
        raise ValueError(f"Unsupported file type: {suffix}")

    frame = frame.copy()
    frame["source_file"] = Path(file_name).name
    return frame


def load_multiple_files(
    uploaded_files: Iterable,
    read_all_sheets: bool = True,
    selected_sheet: str | None = None,
) -> pd.DataFrame:
    """Load and concatenate multiple uploaded files in memory."""

    frames = [
        _load_single_file(file, read_all_sheets=read_all_sheets, selected_sheet=selected_sheet)
        for file in uploaded_files
    ]
    return pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()


def dataframe_to_csv_bytes(df: pd.DataFrame) -> bytes:
    """Serialize a DataFrame to UTF-8 CSV bytes."""

    return df.to_csv(index=False).encode("utf-8")


def dataframe_to_excel_bytes(df: pd.DataFrame) -> bytes:
    """Serialize a DataFrame to an in-memory XLSX file."""

    buffer = BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        df.to_excel(writer, index=False)
    return buffer.getvalue()

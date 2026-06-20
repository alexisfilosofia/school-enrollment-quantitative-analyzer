"""Small helpers that prepare data for Streamlit charts."""

from __future__ import annotations

import pandas as pd


def prepare_bar_chart(df: pd.DataFrame, category_col: str, value_col: str) -> pd.DataFrame:
    """Return a chart-friendly DataFrame indexed by category."""

    if df.empty or category_col not in df.columns or value_col not in df.columns:
        return pd.DataFrame()
    chart_data = df[[category_col, value_col]].copy()
    chart_data[category_col] = chart_data[category_col].astype(str)
    return chart_data.set_index(category_col)


def prepare_line_chart(df: pd.DataFrame, x_col: str, y_col: str) -> pd.DataFrame:
    """Return a chart-friendly DataFrame indexed by the x column."""

    if df.empty or x_col not in df.columns or y_col not in df.columns:
        return pd.DataFrame()
    chart_data = df[[x_col, y_col]].sort_values(x_col).copy()
    chart_data[x_col] = chart_data[x_col].astype(str)
    return chart_data.set_index(x_col)


def prepare_age_distribution(df: pd.DataFrame, age_col: str = "age") -> pd.DataFrame:
    """Return age frequencies for charting."""

    if age_col not in df.columns:
        return pd.DataFrame(columns=["age", "records"])
    age = pd.to_numeric(df[age_col], errors="coerce").dropna().astype(int)
    return age.value_counts().sort_index().rename_axis("age").reset_index(name="records")


def prepare_year_course_heatmap_table(matrix: pd.DataFrame) -> pd.DataFrame:
    """Return a matrix ready for styled display."""

    if matrix.empty:
        return pd.DataFrame()
    return matrix.fillna(0).astype(int)

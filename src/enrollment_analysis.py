"""Enrollment-specific quantitative analysis helpers."""

from __future__ import annotations

import pandas as pd


YEAR_CANDIDATES = ["year", "anio", "ano", "anio_libro", "ano_libro", "ciclo_lectivo"]
COURSE_CANDIDATES = ["course", "curso", "curso_ingreso", "grade_level", "anio_cursada", "ano_cursada"]


def _first_available_column(df: pd.DataFrame, candidates: list[str]) -> str | None:
    for column in candidates:
        if column in df.columns:
            return column
    return None


def detect_year_column(df: pd.DataFrame) -> str | None:
    """Detect the most likely year column."""

    return _first_available_column(df, YEAR_CANDIDATES)


def detect_course_column(df: pd.DataFrame) -> str | None:
    """Detect the most likely course column."""

    return _first_available_column(df, COURSE_CANDIDATES)


def enrollment_by_year(df: pd.DataFrame, year_col: str | None = None) -> pd.DataFrame:
    """Count records by year."""

    year_col = year_col or detect_year_column(df)
    if year_col is None or year_col not in df.columns:
        return pd.DataFrame(columns=["year", "records"])

    result = (
        df.dropna(subset=[year_col])
        .groupby(year_col, dropna=False)
        .size()
        .reset_index(name="records")
        .rename(columns={year_col: "year"})
        .sort_values("year")
        .reset_index(drop=True)
    )
    return result


def enrollment_by_course(df: pd.DataFrame, course_col: str | None = None) -> pd.DataFrame:
    """Count records by course."""

    course_col = course_col or detect_course_column(df)
    if course_col is None or course_col not in df.columns:
        return pd.DataFrame(columns=["course", "records"])

    result = (
        df.dropna(subset=[course_col])
        .groupby(course_col, dropna=False)
        .size()
        .reset_index(name="records")
        .rename(columns={course_col: "course"})
        .sort_values(["records", "course"], ascending=[False, True])
        .reset_index(drop=True)
    )
    return result


def year_course_matrix(
    df: pd.DataFrame,
    year_col: str | None = None,
    course_col: str | None = None,
) -> pd.DataFrame:
    """Build a year x course enrollment matrix."""

    year_col = year_col or detect_year_column(df)
    course_col = course_col or detect_course_column(df)
    if year_col is None or course_col is None or year_col not in df.columns or course_col not in df.columns:
        return pd.DataFrame()

    matrix = pd.crosstab(df[year_col], df[course_col], dropna=False)
    matrix = matrix.sort_index()
    matrix.index.name = "year"
    matrix.columns.name = "course"
    return matrix


def enrollment_growth(enrollment_year: pd.DataFrame) -> pd.DataFrame:
    """Calculate absolute and percentage changes in enrollment by year."""

    if enrollment_year.empty or "records" not in enrollment_year.columns:
        return pd.DataFrame(columns=["year", "records", "absolute_change", "percent_change"])

    growth = enrollment_year.sort_values("year").copy()
    growth["absolute_change"] = growth["records"].diff()
    growth["percent_change"] = growth["records"].pct_change().mul(100).round(2)
    return growth.reset_index(drop=True)


def course_percentages(enrollment_course: pd.DataFrame) -> pd.DataFrame:
    """Calculate course participation percentages."""

    if enrollment_course.empty or "records" not in enrollment_course.columns:
        return pd.DataFrame(columns=["course", "records", "percent"])

    total = enrollment_course["records"].sum()
    percentages = enrollment_course.copy()
    percentages["percent"] = (percentages["records"] / total * 100).round(2) if total else 0
    return percentages.reset_index(drop=True)

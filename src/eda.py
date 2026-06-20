"""General EDA helpers for school enrollment data."""

from __future__ import annotations

import pandas as pd

from src.data_cleaning import missing_values_summary
from src.enrollment_analysis import (
    detect_course_column,
    detect_year_column,
    enrollment_by_course,
    enrollment_by_year,
)


AGE_RANGE_LABELS = ["menor_15", "15_17", "18_20", "21_25", "mayor_25"]

# Identifier patterns to exclude from categorical analysis
IDENTIFIER_PATTERNS = {"id", "student_id", "studentid", "id_", "_id"}
MAX_CARDINALITY_RATIO = 0.5  # Exclude columns where n_unique / n_rows > this ratio
MAX_UNIQUE_VALUES = 50  # Exclude columns with more than this many unique values


def is_identifier_column(column_name: str) -> bool:
    """Check if a column name looks like an identifier."""
    col_lower = column_name.lower()
    return any(pattern in col_lower for pattern in IDENTIFIER_PATTERNS)


def get_valid_categorical_columns(df: pd.DataFrame) -> list[str]:
    """
    Get list of valid categorical columns, excluding identifiers and high-cardinality columns.

    Returns columns that are:
    - Object or string type
    - Not identifiers (student_id, id, etc.)
    - Not high cardinality (n_unique <= 50 AND n_unique/n_rows <= 0.5)
    """
    categorical_columns = [
        column
        for column in df.columns
        if pd.api.types.is_object_dtype(df[column]) or pd.api.types.is_string_dtype(df[column])
    ]

    # Add year column if numeric
    if "year" in df.columns and "year" not in categorical_columns:
        categorical_columns.append("year")

    # Filter out identifiers and high-cardinality columns
    valid_columns = []
    for column in categorical_columns:
        if is_identifier_column(column):
            continue

        n_unique = df[column].nunique(dropna=True)
        n_rows = len(df)

        # Exclude if too many unique values
        if n_unique > MAX_UNIQUE_VALUES or (n_rows > 0 and n_unique / n_rows > MAX_CARDINALITY_RATIO):
            continue

        valid_columns.append(column)

    return valid_columns


def dataset_overview(df: pd.DataFrame) -> dict[str, object]:
    """Return basic dataset-level indicators."""

    year_col = detect_year_column(df)
    course_col = detect_course_column(df)
    duplicate_students = None
    if "student_id" in df.columns:
        duplicate_students = int(df["student_id"].duplicated().sum())

    return {
        "rows": int(len(df)),
        "columns": int(len(df.columns)),
        "detected_years": int(df[year_col].nunique(dropna=True)) if year_col else 0,
        "detected_courses": int(df[course_col].nunique(dropna=True)) if course_col else 0,
        "duplicate_student_ids": duplicate_students,
        "year_column": year_col,
        "course_column": course_col,
    }


def numeric_summary(df: pd.DataFrame) -> pd.DataFrame:
    """Return descriptive statistics for numeric columns."""

    numeric_df = df.select_dtypes(include="number")
    if numeric_df.empty:
        return pd.DataFrame()
    return numeric_df.describe().transpose().reset_index(names="column")


def categorical_summary(df: pd.DataFrame, max_unique: int = 30) -> pd.DataFrame:
    """Return top category counts for categorical columns, excluding identifiers."""

    rows: list[dict[str, object]] = []
    valid_columns = get_valid_categorical_columns(df)
    
    for column in valid_columns:
        counts = df[column].fillna("Sin dato").value_counts(dropna=False).head(max_unique)
        for value, count in counts.items():
            rows.append({"column": column, "value": value, "records": int(count)})
    
    return pd.DataFrame(rows, columns=["column", "value", "records"])


def age_summary(df: pd.DataFrame, age_col: str = "age") -> pd.DataFrame:
    """Return age statistics if an age column exists."""

    if age_col not in df.columns:
        return pd.DataFrame(columns=["metric", "value"])

    age = pd.to_numeric(df[age_col], errors="coerce").dropna()
    if age.empty:
        return pd.DataFrame(columns=["metric", "value"])

    summary = pd.DataFrame(
        [
            {"metric": "media", "value": round(float(age.mean()), 2)},
            {"metric": "mediana", "value": round(float(age.median()), 2)},
            {"metric": "minimo", "value": round(float(age.min()), 2)},
            {"metric": "maximo", "value": round(float(age.max()), 2)},
            {"metric": "desviacion_estandar", "value": round(float(age.std(ddof=1)), 2)},
        ]
    )
    return summary


def age_ranges(df: pd.DataFrame, age_col: str = "age") -> pd.DataFrame:
    """Create enrollment counts by predefined age ranges."""

    if age_col not in df.columns:
        return pd.DataFrame(columns=["age_range", "records"])

    age = pd.to_numeric(df[age_col], errors="coerce")
    ranges = pd.cut(
        age,
        bins=[float("-inf"), 14, 17, 20, 25, float("inf")],
        labels=AGE_RANGE_LABELS,
        right=True,
    )
    result = (
        ranges.value_counts(dropna=False)
        .rename_axis("age_range")
        .reset_index(name="records")
        .sort_values("age_range", key=lambda series: series.astype(str))
        .reset_index(drop=True)
    )
    result["age_range"] = result["age_range"].astype(str).replace({"nan": "sin_dato"})
    return result


def crosstab_summary(df: pd.DataFrame, row_col: str, col_col: str) -> pd.DataFrame:
    """Create a simple cross-tabulation."""

    if row_col not in df.columns or col_col not in df.columns:
        return pd.DataFrame()
    table = pd.crosstab(df[row_col].fillna("Sin dato"), df[col_col].fillna("Sin dato"), dropna=False)
    table.index.name = row_col
    table.columns.name = col_col
    return table


def automatic_summary(df: pd.DataFrame) -> str:
    """Generate a brief Spanish summary from the processed data."""

    overview = dataset_overview(df)
    enrollment_year = enrollment_by_year(df)
    enrollment_course = enrollment_by_course(df)
    missing = missing_values_summary(df)

    lines = [
        f"El dataset procesado contiene {overview['rows']} registros y {overview['columns']} columnas.",
    ]

    if not enrollment_year.empty:
        min_year = enrollment_year["year"].min()
        max_year = enrollment_year["year"].max()
        highest = enrollment_year.loc[enrollment_year["records"].idxmax()]
        lowest = enrollment_year.loc[enrollment_year["records"].idxmin()]
        lines.append(f"Cubre el período {min_year} a {max_year}.")
        lines.append(
            f"El año con mayor matrícula es {highest['year']} con {int(highest['records'])} registros."
        )
        lines.append(
            f"El año con menor matrícula es {lowest['year']} con {int(lowest['records'])} registros."
        )
    else:
        lines.append("No se detectó una columna de año suficiente para calcular evolución anual.")

    if not enrollment_course.empty:
        top_course = enrollment_course.iloc[0]
        lines.append(f"El curso más frecuente es {top_course['course']} con {int(top_course['records'])} registros.")
    else:
        lines.append("No se detectó una columna de curso suficiente para calcular distribución por curso.")

    if "age" in df.columns:
        age = pd.to_numeric(df["age"], errors="coerce").dropna()
        if not age.empty:
            lines.append(f"La edad promedio registrada es {age.mean():.1f} años.")

    missing_with_values = missing[missing["missing_count"] > 0].head(3)
    if not missing_with_values.empty:
        formatted_missing = ", ".join(
            f"{row.column} ({int(row.missing_count)})" for row in missing_with_values.itertuples()
        )
        lines.append(f"Las columnas con más valores faltantes son: {formatted_missing}.")
    else:
        lines.append("No se detectaron valores faltantes en las columnas procesadas.")

    return " ".join(lines)

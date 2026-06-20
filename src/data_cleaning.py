"""Data cleaning helpers for the enrollment analyzer."""

from __future__ import annotations

import re
import unicodedata
from collections import Counter
from typing import Mapping

import pandas as pd


CANONICAL_COLUMN_ALIASES: dict[str, set[str]] = {
    "student_id": {
        "student_id",
        "id_estudiante",
        "id_alumno",
        "id",
        "legajo",
        "matricula_id",
    },
    "year": {
        "year",
        "anio",
        "ano",
        "año",
        "anio_libro",
        "ano_libro",
        "ciclo_lectivo",
        "periodo",
    },
    "course": {
        "course",
        "curso",
        "curso_ingreso",
        "grade_level",
        "anio_cursada",
        "ano_cursada",
        "nivel",
    },
    "age": {
        "age",
        "edad",
        "edad_alumno",
        "edad_estudiante",
    },
    "gender_group": {
        "gender",
        "sexo",
        "genero",
        "género",
        "gender_group",
        "grupo_genero",
    },
    "nationality_group": {
        "nationality",
        "nacionalidad",
        "nationality_group",
        "grupo_nacionalidad",
    },
    "enrollment_status": {
        "enrollment_status",
        "estado",
        "situacion",
        "situacion_matricula",
        "estado_matricula",
    },
    "neighborhood_group": {
        "neighborhood",
        "barrio",
        "neighborhood_group",
        "zona",
        "area",
    },
}


def remove_accents(value: str) -> str:
    """Return a text value without accent marks."""

    normalized = unicodedata.normalize("NFKD", str(value))
    return "".join(char for char in normalized if not unicodedata.combining(char))


def _normalize_single_column_name(column_name: object) -> str:
    normalized = remove_accents(str(column_name)).strip().lower()
    normalized = re.sub(r"[^0-9a-zA-Z]+", "_", normalized)
    normalized = re.sub(r"_+", "_", normalized).strip("_")
    return normalized or "unnamed_column"


def normalize_column_names(df: pd.DataFrame) -> pd.DataFrame:
    """Normalize column names and make duplicates explicit."""

    cleaned = df.copy()
    base_names = [_normalize_single_column_name(column) for column in cleaned.columns]
    seen: Counter[str] = Counter()
    unique_names: list[str] = []

    for name in base_names:
        seen[name] += 1
        if seen[name] == 1:
            unique_names.append(name)
        else:
            unique_names.append(f"{name}_{seen[name]}")

    cleaned.columns = unique_names
    return cleaned


def trim_string_values(df: pd.DataFrame) -> pd.DataFrame:
    """Strip leading/trailing spaces and collapse repeated internal spaces."""

    cleaned = df.copy()
    for column in cleaned.columns:
        if pd.api.types.is_object_dtype(cleaned[column]) or pd.api.types.is_string_dtype(cleaned[column]):
            cleaned[column] = cleaned[column].map(
                lambda value: " ".join(value.split()) if isinstance(value, str) else value
            )
    return cleaned


def _is_empty_column(series: pd.Series) -> bool:
    if series.isna().all():
        return True
    non_missing = series.dropna()
    if non_missing.empty:
        return True
    if non_missing.map(lambda value: isinstance(value, str) and value.strip() == "").all():
        return True
    return False


def drop_empty_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Remove columns with no usable values."""

    empty_columns = [column for column in df.columns if _is_empty_column(df[column])]
    return df.drop(columns=empty_columns)


def infer_column_mapping(columns: list[str] | pd.Index) -> dict[str, str]:
    """Infer a mapping from observed column names to canonical enrollment names."""

    mapping: dict[str, str] = {}
    normalized_columns = {_normalize_single_column_name(column): column for column in columns}

    for canonical_name, aliases in CANONICAL_COLUMN_ALIASES.items():
        normalized_aliases = {_normalize_single_column_name(alias) for alias in aliases}
        for normalized_name, original_name in normalized_columns.items():
            if normalized_name in normalized_aliases:
                mapping[str(original_name)] = canonical_name
                break

    return mapping


def apply_column_mapping(df: pd.DataFrame, mapping: Mapping[str, str]) -> pd.DataFrame:
    """Rename columns with a canonical mapping and keep names unique."""

    renamed = df.rename(columns=dict(mapping)).copy()
    return normalize_column_names(renamed)


def missing_values_summary(df: pd.DataFrame) -> pd.DataFrame:
    """Return missing value counts and percentages by column."""

    total_rows = len(df)
    missing_count = df.isna().sum()
    summary = pd.DataFrame(
        {
            "column": missing_count.index,
            "missing_count": missing_count.values,
            "missing_percent": (
                (missing_count.values / total_rows * 100).round(2) if total_rows else [0] * len(missing_count)
            ),
        }
    )
    return summary.sort_values(["missing_count", "column"], ascending=[False, True]).reset_index(drop=True)


def clean_enrollment_dataset(df: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, object]]:
    """Run the default cleaning workflow and return the cleaned dataset plus metadata."""

    normalized = normalize_column_names(df)
    trimmed = trim_string_values(normalized)
    columns_before_drop = set(trimmed.columns)
    without_empty_columns = drop_empty_columns(trimmed)
    dropped_columns = sorted(columns_before_drop - set(without_empty_columns.columns))
    mapping = infer_column_mapping(without_empty_columns.columns)
    cleaned = apply_column_mapping(without_empty_columns, mapping)

    for numeric_column in ["year", "age"]:
        if numeric_column in cleaned.columns:
            cleaned[numeric_column] = pd.to_numeric(cleaned[numeric_column], errors="coerce")
            if numeric_column == "year":
                cleaned[numeric_column] = cleaned[numeric_column].astype("Int64")

    metadata: dict[str, object] = {
        "dropped_empty_columns": dropped_columns,
        "column_mapping": mapping,
        "missing_values": missing_values_summary(cleaned),
    }
    return cleaned, metadata

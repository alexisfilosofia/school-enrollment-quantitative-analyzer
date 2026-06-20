import pandas as pd

from src.data_cleaning import (
    apply_column_mapping,
    clean_enrollment_dataset,
    drop_empty_columns,
    infer_column_mapping,
    missing_values_summary,
    normalize_column_names,
    remove_accents,
    trim_string_values,
)


def test_remove_accents_and_normalize_column_names():
    df = pd.DataFrame({" Año Libro ": [2023], "Género": ["Femenino"], "Curso Ingreso": ["1er año"]})

    normalized = normalize_column_names(df)

    assert remove_accents("Género y año") == "Genero y ano"
    assert list(normalized.columns) == ["ano_libro", "genero", "curso_ingreso"]


def test_trim_string_values_collapses_extra_spaces():
    df = pd.DataFrame({"course": ["  1er   año  "], "age": [15]})

    trimmed = trim_string_values(df)

    assert trimmed.loc[0, "course"] == "1er año"


def test_drop_empty_columns_and_missing_values_summary():
    df = pd.DataFrame(
        {
            "year": [2022, 2023],
            "empty_a": [None, None],
            "empty_b": [" ", ""],
            "course": ["1er año", None],
        }
    )

    cleaned = drop_empty_columns(df)
    missing = missing_values_summary(cleaned)

    assert list(cleaned.columns) == ["year", "course"]
    assert missing.loc[missing["column"] == "course", "missing_count"].iloc[0] == 1


def test_infer_and_apply_column_mapping():
    df = pd.DataFrame({"ano_libro": [2021], "curso_ingreso": ["2do año"], "edad": [14]})

    mapping = infer_column_mapping(df.columns)
    mapped = apply_column_mapping(df, mapping)

    assert mapping == {"ano_libro": "year", "curso_ingreso": "course", "edad": "age"}
    assert list(mapped.columns) == ["year", "course", "age"]


def test_clean_enrollment_dataset_returns_canonical_columns_and_metadata():
    df = pd.DataFrame(
        {
            " Año Libro ": ["2024", "2024"],
            " Curso Ingreso ": [" 1er año ", "2do año"],
            "Edad": ["15", ""],
            "Columna Vacía": [None, None],
        }
    )

    cleaned, metadata = clean_enrollment_dataset(df)

    assert {"year", "course", "age"}.issubset(cleaned.columns)
    assert "columna_vacia" in metadata["dropped_empty_columns"]
    assert cleaned.loc[0, "course"] == "1er año"

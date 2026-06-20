import pandas as pd

from src.eda import (
    age_ranges,
    automatic_summary,
    categorical_summary,
    crosstab_summary,
    dataset_overview,
    numeric_summary,
)


def sample_df():
    return pd.DataFrame(
        {
            "student_id": ["A", "B", "C", "D"],
            "year": [2022, 2022, 2023, 2023],
            "course": ["1er año", "2do año", "1er año", "3er año"],
            "age": [14, 16, 19, 27],
            "gender_group": ["Femenino", "Masculino", "Femenino", None],
        }
    )


def test_dataset_overview():
    overview = dataset_overview(sample_df())

    assert overview["rows"] == 4
    assert overview["columns"] == 5
    assert overview["detected_years"] == 2
    assert overview["detected_courses"] == 3


def test_numeric_and_categorical_summary():
    numeric = numeric_summary(sample_df())
    categorical = categorical_summary(sample_df())

    assert "age" in set(numeric["column"])
    assert "course" in set(categorical["column"])


def test_age_ranges():
    result = age_ranges(sample_df())

    assert {"menor_15", "15_17", "18_20", "mayor_25"}.issubset(set(result["age_range"]))


def test_crosstab_summary():
    table = crosstab_summary(sample_df(), "year", "course")

    assert table.loc[2022, "1er año"] == 1
    assert table.loc[2023, "3er año"] == 1


def test_automatic_summary_is_spanish_and_data_driven():
    summary = automatic_summary(sample_df())

    assert "El dataset procesado contiene 4 registros" in summary
    assert "curso más frecuente" in summary
    assert "edad promedio" in summary

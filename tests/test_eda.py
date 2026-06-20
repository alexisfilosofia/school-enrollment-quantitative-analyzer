import pandas as pd

from src.eda import (
    age_ranges,
    automatic_summary,
    categorical_summary,
    crosstab_summary,
    dataset_overview,
    get_valid_categorical_columns,
    is_identifier_column,
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


def sample_df_with_high_cardinality():
    """Create a sample DataFrame with high-cardinality identifier columns."""
    base_df = sample_df()
    # Add columns that should be excluded
    base_df["id_estudiante"] = [f"ID_{i:05d}" for i in range(len(base_df))]
    base_df["phone_number"] = ["123456789", "987654321", "555555555", "111111111"]
    return base_df


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


def test_identifier_column_detection():
    """Test that identifier patterns are detected."""
    assert is_identifier_column("student_id")
    assert is_identifier_column("id_estudiante")
    assert is_identifier_column("ID")
    assert is_identifier_column("studentid")
    assert is_identifier_column("user_id")
    assert not is_identifier_column("course")
    assert not is_identifier_column("gender_group")


def test_valid_categorical_columns_excludes_identifiers():
    """Test that student_id and similar identifiers are excluded."""
    df = sample_df_with_high_cardinality()
    valid_cols = get_valid_categorical_columns(df)
    
    # student_id should be excluded (it's in categorical_columns but is an identifier)
    assert "student_id" not in valid_cols
    # id_estudiante should be excluded
    assert "id_estudiante" not in valid_cols
    # course and gender_group should be included
    assert "course" in valid_cols
    assert "gender_group" in valid_cols


def test_valid_categorical_columns_excludes_high_cardinality():
    """Test that high-cardinality columns are excluded."""
    df = pd.DataFrame({
        "course": ["A", "B", "C", "A", "B", "C"],
        "almost_unique": ["X1", "X2", "X3", "X4", "X5", "X6"],  # n_unique = n_rows, should be excluded
        "gender": ["M", "F", "M", "F", "M", "F"],
    })
    valid_cols = get_valid_categorical_columns(df)
    
    # course and gender should be included
    assert "course" in valid_cols
    assert "gender" in valid_cols
    # almost_unique should be excluded (n_unique / n_rows = 1.0 > 0.5)
    assert "almost_unique" not in valid_cols


def test_valid_categorical_columns_respects_max_unique():
    """Test that columns with > 50 unique values are excluded."""
    df = pd.DataFrame(
        {
            "course": ["A", "B"] * 30,
            "almost_unique": [f"val_{i}" for i in range(60)],
        }
    )

    valid_cols = get_valid_categorical_columns(df)

    # Only course should be included
    assert "course" in valid_cols
    # High-cardinality columns should be excluded
    for col in df.columns:
        if col != "course":
            assert col not in valid_cols

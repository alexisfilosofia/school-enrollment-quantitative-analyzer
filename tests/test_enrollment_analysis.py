import pandas as pd

from src.enrollment_analysis import (
    course_percentages,
    detect_course_column,
    detect_year_column,
    enrollment_by_course,
    enrollment_by_year,
    enrollment_growth,
    year_course_matrix,
)


def sample_df():
    return pd.DataFrame(
        {
            "year": [2022, 2022, 2023, 2023, 2023],
            "course": ["1er año", "2do año", "1er año", "1er año", "3er año"],
            "age": [13, 14, 14, 15, 16],
        }
    )


def test_detect_year_and_course_columns():
    df = sample_df()

    assert detect_year_column(df) == "year"
    assert detect_course_column(df) == "course"


def test_enrollment_by_year_counts_records():
    result = enrollment_by_year(sample_df())

    assert result.to_dict("records") == [
        {"year": 2022, "records": 2},
        {"year": 2023, "records": 3},
    ]


def test_enrollment_by_course_counts_records():
    result = enrollment_by_course(sample_df())

    top = result.iloc[0]
    assert top["course"] == "1er año"
    assert top["records"] == 3


def test_year_course_matrix():
    matrix = year_course_matrix(sample_df())

    assert matrix.loc[2022, "1er año"] == 1
    assert matrix.loc[2023, "1er año"] == 2
    assert matrix.loc[2023, "3er año"] == 1


def test_enrollment_growth_and_course_percentages():
    yearly = enrollment_by_year(sample_df())
    growth = enrollment_growth(yearly)
    percentages = course_percentages(enrollment_by_course(sample_df()))

    assert growth.loc[1, "absolute_change"] == 1
    assert growth.loc[1, "percent_change"] == 50.0
    assert round(percentages["percent"].sum(), 0) == 100

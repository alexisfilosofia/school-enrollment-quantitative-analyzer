"""Streamlit app for quantitative school enrollment analysis."""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import streamlit as st

from src.data_cleaning import clean_enrollment_dataset, missing_values_summary
from src.eda import (
    AGE_RANGE_LABELS,
    age_ranges,
    age_summary,
    automatic_summary,
    categorical_summary,
    crosstab_summary,
    dataset_overview,
    get_valid_categorical_columns,
    numeric_summary,
)
from src.enrollment_analysis import (
    course_percentages,
    detect_course_column,
    detect_year_column,
    enrollment_by_course,
    enrollment_by_year,
    enrollment_growth,
    year_course_matrix,
)
from src.export_utils import build_export_tables, build_zip_export, make_csv_download
from src.io_utils import load_csv, load_multiple_files, read_excel_sheets
from src.translations import (
    DEFAULT_LANGUAGE,
    SUPPORTED_LANGUAGES,
    label_age_range,
    label_column,
    label_columns,
    label_crosstab,
    normalize_language,
    t,
)
from src.visualization import prepare_age_distribution, prepare_bar_chart, prepare_line_chart


BASE_DIR = Path(__file__).resolve().parent
SAMPLE_DATA_PATH = BASE_DIR / "data" / "sample_enrollment_data.csv"


st.set_page_config(
    page_title="School Enrollment Quantitative Analyzer",
    page_icon="📊",
    layout="wide",
)


def apply_page_styles() -> None:
    """Apply a small visual layer aligned with the portfolio palette."""

    st.markdown(
        """
        <style>
        .stApp {
            background: #f7f5ef;
            color: #1f2933;
        }
        .block-container {
            padding-top: 2.4rem;
            padding-bottom: 3rem;
            max-width: 1180px;
        }
        [data-testid="stSidebar"] {
            background: #ffffff;
            border-right: 1px solid #d8d3c7;
        }
        h1, h2, h3 {
            color: #101923;
            letter-spacing: 0;
        }
        h1 {
            font-size: clamp(2.1rem, 4vw, 3.7rem);
            line-height: 1.04;
        }
        h2 {
            border-top: 1px solid #d8d3c7;
            padding-top: 1.5rem;
            margin-top: 2rem;
        }
        div[data-testid="stMetric"] {
            background: #ffffff;
            border: 1px solid #d8d3c7;
            border-radius: 14px;
            padding: 1rem;
            box-shadow: 0 14px 35px rgba(23, 74, 124, 0.08);
        }
        div[data-testid="stAlert"] {
            border-radius: 12px;
        }
        .privacy-note {
            background: #ffffff;
            border: 1px solid #d8d3c7;
            border-left: 5px solid #174a7c;
            border-radius: 14px;
            padding: 1rem 1.1rem;
            box-shadow: 0 14px 35px rgba(23, 74, 124, 0.07);
            margin: 1rem 0 1.5rem 0;
        }
        .section-note {
            color: #607080;
            font-size: 0.95rem;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def normalize_dataframe_for_display(data: object) -> object:
    """Normalize display-only DataFrames before sending them to Streamlit."""

    if not isinstance(data, pd.DataFrame):
        return data

    safe_df = data.copy()
    safe_df.columns = [str(column) for column in safe_df.columns]
    for column in safe_df.columns:
        if safe_df[column].dtype == "object":
            non_null = safe_df[column].dropna()
            if non_null.map(type).nunique() > 1:
                safe_df[column] = safe_df[column].astype(str)
    return safe_df


def safe_dataframe(data: object, **kwargs: object) -> None:
    """
    Safely render a DataFrame, normalizing types if needed.

    Attempts to render with st.dataframe. If serialization fails,
    converts columns to safe types and retries.
    """
    render_kwargs = dict(kwargs)
    if "use_container_width" in render_kwargs and "width" not in render_kwargs:
        render_kwargs["width"] = "stretch" if render_kwargs.pop("use_container_width") else "content"

    display_data = normalize_dataframe_for_display(data)
    try:
        st.dataframe(display_data, **render_kwargs)
    except (ValueError, TypeError, ImportError):
        if not isinstance(display_data, pd.DataFrame):
            raise

        fallback_df = display_data.copy()
        for column in fallback_df.columns:
            if fallback_df[column].dtype == "object":
                fallback_df[column] = fallback_df[column].astype(str)
        st.dataframe(fallback_df, **render_kwargs)


def select_language() -> str:
    """Render the sidebar language selector and persist its value."""

    if "language" not in st.session_state:
        st.session_state.language = DEFAULT_LANGUAGE

    current_language = normalize_language(st.session_state.language)
    selected_language = st.sidebar.selectbox(
        t("sidebar_language", current_language),
        options=list(SUPPORTED_LANGUAGES),
        index=list(SUPPORTED_LANGUAGES).index(current_language),
        format_func=lambda code: t(f"language_{code}", current_language),
    )
    if selected_language != current_language:
        st.session_state.language = selected_language
        st.rerun()

    st.session_state.language = selected_language
    return selected_language


def load_input_data(lang: str) -> tuple[pd.DataFrame | None, str]:
    """Render the sidebar and load data in memory."""

    st.sidebar.header(t("sidebar_upload_header", lang))
    st.sidebar.caption(t("sidebar_upload_caption", lang))

    uploaded_files = st.sidebar.file_uploader(
        t("upload_files", lang),
        type=["csv", "xlsx", "xls"],
        accept_multiple_files=True,
        help=t("upload_help", lang),
    )
    use_sample = st.sidebar.checkbox(t("use_sample", lang), value=True)
    read_all_sheets = st.sidebar.checkbox(t("read_all_sheets", lang), value=True)

    selected_sheet: str | None = None
    excel_files = [
        file for file in uploaded_files if Path(getattr(file, "name", "")).suffix.lower() in {".xlsx", ".xls"}
    ]

    if len(excel_files) == 1 and not read_all_sheets:
        try:
            excel_files[0].seek(0)
            sheet_names = read_excel_sheets(excel_files[0])
            excel_files[0].seek(0)
            selected_sheet = st.sidebar.selectbox(t("select_sheet", lang), sheet_names)
        except Exception as exc:  # pragma: no cover - defensive UI path
            st.sidebar.warning(t("excel_sheet_error", lang, error=exc))

    if uploaded_files:
        try:
            for uploaded_file in uploaded_files:
                uploaded_file.seek(0)
            data = load_multiple_files(
                uploaded_files,
                read_all_sheets=read_all_sheets,
                selected_sheet=selected_sheet,
            )
            return data, t("source_uploaded_files", lang)
        except Exception as exc:
            st.error(t("load_files_error", lang, error=exc))
            return None, t("source_error", lang)

    if use_sample:
        return load_csv(SAMPLE_DATA_PATH), t("source_sample_dataset", lang)

    return None, t("source_no_data", lang)


def format_missing_table(table: pd.DataFrame, lang: str) -> pd.DataFrame:
    """Translate missing value table columns for display."""

    return label_columns(table, lang)


def add_age_range_column(df: pd.DataFrame) -> pd.DataFrame:
    """Add an age range column when age is available."""

    enriched = df.copy()
    if "age" in enriched.columns:
        age = pd.to_numeric(enriched["age"], errors="coerce")
        enriched["age_range"] = pd.cut(
            age,
            bins=[float("-inf"), 14, 17, 20, 25, float("inf")],
            labels=AGE_RANGE_LABELS,
            right=True,
        ).astype("object")
        enriched["age_range"] = enriched["age_range"].fillna("sin_dato")
    return enriched


def display_general_eda(cleaned: pd.DataFrame, metadata: dict[str, object], lang: str) -> None:
    """Render general EDA information."""

    st.header(t("general_eda", lang))
    overview = dataset_overview(cleaned)
    metric_cols = st.columns(4)
    metric_cols[0].metric(t("total_records", lang), f"{overview['rows']:,}")
    metric_cols[1].metric(t("column_count", lang), f"{overview['columns']:,}")
    metric_cols[2].metric(t("detected_years", lang), f"{overview['detected_years']:,}")
    metric_cols[3].metric(t("detected_courses", lang), f"{overview['detected_courses']:,}")

    duplicate_student_ids = overview.get("duplicate_student_ids")
    if duplicate_student_ids is not None:
        st.caption(t("duplicate_student_ids", lang, count=f"{duplicate_student_ids:,}"))

    dropped_columns = metadata.get("dropped_empty_columns", [])
    if dropped_columns:
        st.info(t("dropped_empty_columns", lang, columns=", ".join(str(column) for column in dropped_columns)))
    else:
        st.caption(t("no_empty_columns", lang))

    tab_preview, tab_missing, tab_types = st.tabs(
        [t("tab_preview", lang), t("tab_missing", lang), t("tab_types", lang)]
    )
    with tab_preview:
        safe_dataframe(cleaned.head(20), use_container_width=True)
    with tab_missing:
        missing_table = metadata.get("missing_values")
        if isinstance(missing_table, pd.DataFrame):
            safe_dataframe(format_missing_table(missing_table, lang), use_container_width=True)
    with tab_types:
        dtype_table = pd.DataFrame(
            {label_column("column", lang): cleaned.dtypes.index, t("tab_types", lang): cleaned.dtypes.astype(str).values}
        )
        safe_dataframe(dtype_table, use_container_width=True)


def display_enrollment_by_year(cleaned: pd.DataFrame, lang: str) -> pd.DataFrame:
    """Render annual enrollment analysis and return the table."""

    st.header(t("enrollment_by_year", lang))
    table = enrollment_by_year(cleaned)
    growth = enrollment_growth(table)

    if table.empty:
        st.warning(t("no_year_column", lang))
        return table

    high = table.loc[table["records"].idxmax()]
    low = table.loc[table["records"].idxmin()]
    metric_cols = st.columns(2)
    metric_cols[0].metric(
        t("highest_enrollment_year", lang),
        f"{high['year']}",
        t("records_delta", lang, count=int(high["records"])),
    )
    metric_cols[1].metric(
        t("lowest_enrollment_year", lang),
        f"{low['year']}",
        t("records_delta", lang, count=int(low["records"])),
    )

    display_table = label_columns(table, lang)
    chart_data = prepare_line_chart(display_table, label_column("year", lang), label_column("records", lang))
    st.line_chart(chart_data)
    safe_dataframe(display_table, use_container_width=True)

    st.subheader(t("year_over_year_change", lang))
    display_growth = label_columns(growth, lang)
    safe_dataframe(display_growth, use_container_width=True)
    return table


def display_enrollment_by_course(cleaned: pd.DataFrame, lang: str) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Render course-level analysis and return course table and matrix."""

    st.header(t("enrollment_by_course", lang))
    course_table = enrollment_by_course(cleaned)
    matrix = year_course_matrix(cleaned)

    if course_table.empty:
        st.warning(t("no_course_column", lang))
        return course_table, matrix

    display_course = label_columns(course_table, lang)
    chart_data = prepare_bar_chart(display_course, label_column("course", lang), label_column("records", lang))
    st.bar_chart(chart_data)
    safe_dataframe(display_course, use_container_width=True)

    percentages = label_columns(course_percentages(course_table), lang)
    st.subheader(t("course_percentages", lang))
    safe_dataframe(percentages, use_container_width=True)

    st.subheader(t("year_course_matrix", lang))
    if matrix.empty:
        st.info(t("year_course_matrix_requires_columns", lang))
    else:
        display_matrix = matrix.copy()
        display_matrix.index.name = label_column("year", lang)
        display_matrix.columns.name = label_column("course", lang)
        try:
            styled_matrix = display_matrix.style.background_gradient(cmap="Blues", axis=None)
            safe_dataframe(styled_matrix, use_container_width=True)
        except (ImportError, ValueError, AttributeError):
            # Fallback when Styler rendering fails (e.g., missing matplotlib on Streamlit Cloud)
            safe_dataframe(display_matrix, use_container_width=True)

    return course_table, matrix


def display_age_analysis(cleaned: pd.DataFrame, lang: str) -> pd.DataFrame:
    """Render age analysis and return the age summary table."""

    st.header(t("age_analysis", lang))
    if "age" not in cleaned.columns:
        st.info(t("no_age_column", lang))
        return pd.DataFrame()

    summary = age_summary(cleaned)
    if summary.empty:
        st.info(t("age_not_numeric", lang))
        return summary

    metrics = {row.metric: row.value for row in summary.itertuples()}
    metric_cols = st.columns(5)
    metric_cols[0].metric(t("mean", lang), metrics.get("media", t("no_data", lang)))
    metric_cols[1].metric(t("median", lang), metrics.get("mediana", t("no_data", lang)))
    metric_cols[2].metric(t("minimum", lang), metrics.get("minimo", t("no_data", lang)))
    metric_cols[3].metric(t("maximum", lang), metrics.get("maximo", t("no_data", lang)))
    metric_cols[4].metric(t("std_dev", lang), metrics.get("desviacion_estandar", t("no_data", lang)))

    age_distribution = prepare_age_distribution(cleaned)
    if not age_distribution.empty:
        display_age_distribution = label_columns(age_distribution, lang)
        st.bar_chart(display_age_distribution.set_index(label_column("age", lang)))

    year_col = detect_year_column(cleaned)
    course_col = detect_course_column(cleaned)
    tab_ranges, tab_year, tab_course, tab_outliers = st.tabs(
        [t("age_ranges", lang), t("age_by_year", lang), t("age_by_course", lang), t("outliers", lang)]
    )
    with tab_ranges:
        display_ranges = age_ranges(cleaned)
        if not display_ranges.empty:
            display_ranges = display_ranges.assign(age_range=display_ranges["age_range"].map(lambda value: label_age_range(value, lang)))
        display_ranges = label_columns(display_ranges, lang)
        safe_dataframe(display_ranges, use_container_width=True)
    with tab_year:
        if year_col:
            by_year = (
                cleaned.assign(age=pd.to_numeric(cleaned["age"], errors="coerce"))
                .dropna(subset=["age", year_col])
                .groupby(year_col)["age"]
                .mean()
                .round(2)
                .reset_index()
                .rename(columns={year_col: "year", "age": "average_age"})
            )
            safe_dataframe(label_columns(by_year, lang), use_container_width=True)
        else:
            st.info(t("no_year_column", lang))
    with tab_course:
        if course_col:
            by_course = (
                cleaned.assign(age=pd.to_numeric(cleaned["age"], errors="coerce"))
                .dropna(subset=["age", course_col])
                .groupby(course_col)["age"]
                .mean()
                .round(2)
                .reset_index()
                .rename(columns={course_col: "course", "age": "average_age"})
            )
            safe_dataframe(label_columns(by_course, lang), use_container_width=True)
        else:
            st.info(t("no_course_column", lang))
    with tab_outliers:
        age = pd.to_numeric(cleaned["age"], errors="coerce")
        quartile_1 = age.quantile(0.25)
        quartile_3 = age.quantile(0.75)
        iqr = quartile_3 - quartile_1
        lower = quartile_1 - 1.5 * iqr
        upper = quartile_3 + 1.5 * iqr
        outlier_count = int(((age < lower) | (age > upper)).sum())
        st.metric(t("possible_age_outliers", lang), outlier_count)
        st.caption(t("iqr_caption", lang, lower=lower, upper=upper))

    return summary


def display_categorical_analysis(cleaned: pd.DataFrame, lang: str) -> pd.DataFrame:
    """Render categorical distributions and return a summary table."""

    st.header(t("categorical_analysis", lang))
    categorical_report = categorical_summary(cleaned)
    valid_categorical_columns = get_valid_categorical_columns(cleaned)

    if not valid_categorical_columns:
        st.info(t("no_categorical_variables", lang))
        return categorical_report

    selected_column = st.sidebar.selectbox(
        t("categorical_column_select", lang),
        valid_categorical_columns,
        format_func=lambda column: label_column(column, lang),
    )
    
    # Build distribution table with normalized types
    distribution = (
        cleaned[selected_column]
        .fillna(t("no_data", lang))
        .astype(str)
        .value_counts(dropna=False)
        .reset_index()
    )
    distribution.columns = ["category", "frequency"]
    distribution["percent"] = (
        (distribution["frequency"] / distribution["frequency"].sum() * 100).round(2)
    )
    distribution = distribution.reset_index(drop=True)

    st.subheader(t("distribution_of", lang, column=label_column(selected_column, lang)))
    if "category" in distribution.columns and "frequency" in distribution.columns:
        try:
            display_distribution = label_columns(distribution, lang)
            st.bar_chart(display_distribution.set_index(label_column("category", lang))[label_column("frequency", lang)])
        except (ValueError, TypeError):
            pass  # Chart may fail with certain types, but don't crash
    
    safe_dataframe(label_columns(distribution, lang), use_container_width=True)

    st.subheader(t("categorical_summary", lang))
    display_report = categorical_report.copy()
    if "value" in display_report.columns:
        display_report["value"] = display_report["value"].replace({"Sin dato": t("no_data", lang)})
    display_report = label_columns(display_report, lang)
    safe_dataframe(display_report, use_container_width=True)
    return categorical_report


def display_descriptive_statistics(cleaned: pd.DataFrame, missing_report: pd.DataFrame, lang: str) -> None:
    """Render descriptive statistics section."""

    st.header(t("descriptive_statistics", lang))
    tab_numeric, tab_categorical, tab_missing, tab_cardinality = st.tabs(
        [t("numeric_variables", lang), t("categorical_variables", lang), t("tab_missing", lang), t("cardinality", lang)]
    )
    with tab_numeric:
        numeric = numeric_summary(cleaned)
        if numeric.empty:
            st.info(t("no_numeric_variables", lang))
        else:
            safe_dataframe(label_columns(numeric, lang), use_container_width=True)
    with tab_categorical:
        categorical = categorical_summary(cleaned, max_unique=10)
        if categorical.empty:
            st.info(t("no_categorical_variables", lang))
        else:
            display_categorical = categorical.copy()
            if "value" in display_categorical.columns:
                display_categorical["value"] = display_categorical["value"].replace({"Sin dato": t("no_data", lang)})
            safe_dataframe(label_columns(display_categorical, lang), use_container_width=True)
    with tab_missing:
        safe_dataframe(format_missing_table(missing_report, lang), use_container_width=True)
    with tab_cardinality:
        cardinality = pd.DataFrame(
            {
                "column": cleaned.columns,
                "unique_values": [cleaned[column].nunique(dropna=True) for column in cleaned.columns],
            }
        )
        safe_dataframe(label_columns(cardinality, lang), use_container_width=True)


def display_crosstabs(cleaned: pd.DataFrame, lang: str) -> dict[str, pd.DataFrame]:
    """Render available cross-tabulations and return them for export."""

    st.header(t("crosstabs", lang))
    enriched = add_age_range_column(cleaned)
    year_col = detect_year_column(enriched)
    course_col = detect_course_column(enriched)
    available_crosstabs: dict[str, tuple[str, str]] = {}

    if year_col and course_col:
        available_crosstabs["year_course"] = (year_col, course_col)
    if year_col and "age_range" in enriched.columns:
        available_crosstabs["year_age_range"] = (year_col, "age_range")
    if course_col and "age_range" in enriched.columns:
        available_crosstabs["course_age_range"] = (course_col, "age_range")
    if year_col and "gender_group" in enriched.columns:
        available_crosstabs["year_gender"] = (year_col, "gender_group")
    if course_col and "gender_group" in enriched.columns:
        available_crosstabs["course_gender"] = (course_col, "gender_group")
    if year_col and "nationality_group" in enriched.columns:
        available_crosstabs["year_nationality"] = (year_col, "nationality_group")

    if not available_crosstabs:
        st.info(t("no_crosstabs", lang))
        return {}

    selected_tables = st.multiselect(
        t("select_crosstabs", lang),
        options=list(available_crosstabs.keys()),
        default=list(available_crosstabs.keys())[:3],
        format_func=lambda key: label_crosstab(key, lang),
    )
    rendered_tables: dict[str, pd.DataFrame] = {}
    for key in selected_tables:
        row_col, col_col = available_crosstabs[key]
        table = crosstab_summary(enriched, row_col, col_col)
        label = label_crosstab(key, lang)
        rendered_tables[key] = table
        st.subheader(label)
        display_table = table.copy()
        if row_col == "age_range":
            display_table.index = display_table.index.map(lambda value: label_age_range(value, lang))
        if col_col == "age_range":
            display_table.columns = [label_age_range(value, lang) for value in display_table.columns]
        display_table.index.name = label_column(row_col, lang)
        display_table.columns.name = label_column(col_col, lang)
        safe_dataframe(display_table, use_container_width=True)
        st.download_button(
            t("download_crosstab", lang, label=label.lower()),
            data=make_csv_download(table.reset_index()),
            file_name=f"{key}.csv",
            mime="text/csv",
        )

    return rendered_tables


def display_exports(
    cleaned: pd.DataFrame,
    enrollment_year: pd.DataFrame,
    enrollment_course: pd.DataFrame,
    matrix: pd.DataFrame,
    missing_report: pd.DataFrame,
    age_report: pd.DataFrame,
    categorical_report: pd.DataFrame,
    lang: str,
) -> None:
    """Render download buttons for exportable outputs."""

    st.header(t("exports", lang))
    tables = build_export_tables(
        cleaned_dataset=cleaned,
        enrollment_year=enrollment_year,
        enrollment_course=enrollment_course,
        matrix=matrix,
        missing_report=missing_report,
        age_report=age_report,
        categorical_report=categorical_report,
    )
    export_columns = st.columns(2)
    labels = {
        "cleaned_dataset.csv": t("download_cleaned_dataset", lang),
        "enrollment_by_year.csv": t("download_enrollment_by_year", lang),
        "enrollment_by_course.csv": t("download_enrollment_by_course", lang),
        "year_course_matrix.csv": t("download_year_course_matrix", lang),
        "missing_values_report.csv": t("download_missing_values", lang),
        "age_summary.csv": t("download_age_summary", lang),
        "categorical_summary.csv": t("download_categorical_summary", lang),
    }
    for index, (filename, table) in enumerate(tables.items()):
        export_columns[index % 2].download_button(
            labels.get(filename, t("download_file", lang, filename=filename)),
            data=make_csv_download(table),
            file_name=filename,
            mime="text/csv",
        )

    st.download_button(
        t("download_zip", lang),
        data=build_zip_export(tables),
        file_name="full_analysis_summary.zip",
        mime="application/zip",
    )


def main() -> None:
    """Run the Streamlit app."""

    apply_page_styles()
    lang = select_language()
    st.title(t("app_title", lang))
    st.markdown(t("app_description", lang))
    st.markdown(
        f'<div class="privacy-note">{t("privacy_note", lang)}</div>',
        unsafe_allow_html=True,
    )

    raw_data, source_label = load_input_data(lang)
    if raw_data is None or raw_data.empty:
        st.info(t("empty_start", lang))
        return None

    st.sidebar.success(t("loaded_source", lang, source=source_label))

    with st.spinner(t("cleaning_spinner", lang)):
        cleaned, metadata = clean_enrollment_dataset(raw_data)

    if cleaned.empty:
        st.warning(t("empty_after_cleaning", lang))
        return None

    missing_report = missing_values_summary(cleaned)
    display_general_eda(cleaned, metadata, lang)
    enrollment_year = display_enrollment_by_year(cleaned, lang)
    enrollment_course, matrix = display_enrollment_by_course(cleaned, lang)
    age_report = display_age_analysis(cleaned, lang)
    categorical_report = display_categorical_analysis(cleaned, lang)
    display_descriptive_statistics(cleaned, missing_report, lang)
    display_crosstabs(cleaned, lang)

    st.header(t("automatic_summary", lang))
    st.write(automatic_summary(cleaned, lang=lang))

    display_exports(
        cleaned=cleaned,
        enrollment_year=enrollment_year,
        enrollment_course=enrollment_course,
        matrix=matrix,
        missing_report=missing_report,
        age_report=age_report,
        categorical_report=categorical_report,
        lang=lang,
    )
    return None


if __name__ == "__main__":
    main()

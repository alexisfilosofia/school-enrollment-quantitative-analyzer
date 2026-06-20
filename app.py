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
from src.visualization import prepare_age_distribution, prepare_bar_chart, prepare_line_chart


BASE_DIR = Path(__file__).resolve().parent
SAMPLE_DATA_PATH = BASE_DIR / "data" / "sample_enrollment_data.csv"


st.set_page_config(
    page_title="Analizador cuantitativo de matrícula escolar",
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


def safe_dataframe(df: pd.DataFrame, **kwargs: object) -> None:
    """
    Safely render a DataFrame, normalizing types if needed.
    
    Attempts to render with st.dataframe. If serialization fails,
    converts columns to safe types and retries.
    """
    try:
        st.dataframe(df, **kwargs)
    except (ValueError, TypeError, ImportError):
        # Normalize DataFrame for Arrow serialization
        safe_df = df.copy()
        safe_df.columns = [str(c) for c in safe_df.columns]
        for col in safe_df.columns:
            if safe_df[col].dtype == "object":
                safe_df[col] = safe_df[col].astype(str)
        st.dataframe(safe_df, **kwargs)


def load_input_data() -> tuple[pd.DataFrame | None, str]:
    """Render the Spanish sidebar and load data in memory."""

    st.sidebar.header("Carga de archivos")
    st.sidebar.caption("Subí archivos CSV o Excel, o usá el dataset sintético incluido.")

    uploaded_files = st.sidebar.file_uploader(
        "Cargar archivos",
        type=["csv", "xlsx", "xls"],
        accept_multiple_files=True,
        help="Los archivos se procesan en memoria durante la sesión.",
    )
    use_sample = st.sidebar.checkbox("Usar dataset de ejemplo", value=True)
    read_all_sheets = st.sidebar.checkbox("Leer todas las hojas de Excel", value=True)

    selected_sheet: str | None = None
    excel_files = [
        file for file in uploaded_files if Path(getattr(file, "name", "")).suffix.lower() in {".xlsx", ".xls"}
    ]

    if len(excel_files) == 1 and not read_all_sheets:
        try:
            excel_files[0].seek(0)
            sheet_names = read_excel_sheets(excel_files[0])
            excel_files[0].seek(0)
            selected_sheet = st.sidebar.selectbox("Seleccionar hoja", sheet_names)
        except Exception as exc:  # pragma: no cover - defensive UI path
            st.sidebar.warning(f"No se pudieron leer las hojas del Excel: {exc}")

    if uploaded_files:
        try:
            for uploaded_file in uploaded_files:
                uploaded_file.seek(0)
            data = load_multiple_files(
                uploaded_files,
                read_all_sheets=read_all_sheets,
                selected_sheet=selected_sheet,
            )
            return data, "archivos cargados"
        except Exception as exc:
            st.error(f"No se pudieron cargar los archivos: {exc}")
            return None, "error"

    if use_sample:
        return load_csv(SAMPLE_DATA_PATH), "dataset sintético de ejemplo"

    return None, "sin datos"


def format_missing_table(table: pd.DataFrame) -> pd.DataFrame:
    """Translate missing value table columns for display."""

    return table.rename(
        columns={
            "column": "Columna",
            "missing_count": "Valores faltantes",
            "missing_percent": "Porcentaje faltante",
        }
    )


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


def display_general_eda(cleaned: pd.DataFrame, metadata: dict[str, object]) -> None:
    """Render general EDA information."""

    st.header("Exploración general de datos")
    overview = dataset_overview(cleaned)
    metric_cols = st.columns(4)
    metric_cols[0].metric("Total de registros", f"{overview['rows']:,}")
    metric_cols[1].metric("Cantidad de columnas", f"{overview['columns']:,}")
    metric_cols[2].metric("Años detectados", f"{overview['detected_years']:,}")
    metric_cols[3].metric("Cursos detectados", f"{overview['detected_courses']:,}")

    duplicate_student_ids = overview.get("duplicate_student_ids")
    if duplicate_student_ids is not None:
        st.caption(f"Duplicados detectados en student_id: {duplicate_student_ids:,}")

    dropped_columns = metadata.get("dropped_empty_columns", [])
    if dropped_columns:
        st.info("Columnas vacías eliminadas: " + ", ".join(str(column) for column in dropped_columns))
    else:
        st.caption("No se detectaron columnas completamente vacías.")

    tab_preview, tab_missing, tab_types = st.tabs(
        ["Vista previa", "Valores faltantes", "Tipos de datos"]
    )
    with tab_preview:
        safe_dataframe(cleaned.head(20), use_container_width=True)
    with tab_missing:
        missing_table = metadata.get("missing_values")
        if isinstance(missing_table, pd.DataFrame):
            safe_dataframe(format_missing_table(missing_table), use_container_width=True)
    with tab_types:
        dtype_table = pd.DataFrame(
            {"Columna": cleaned.dtypes.index, "Tipo de dato": cleaned.dtypes.astype(str).values}
        )
        safe_dataframe(dtype_table, use_container_width=True)


def display_enrollment_by_year(cleaned: pd.DataFrame) -> pd.DataFrame:
    """Render annual enrollment analysis and return the table."""

    st.header("Matrícula por año")
    table = enrollment_by_year(cleaned)
    growth = enrollment_growth(table)

    if table.empty:
        st.warning("No se detectó una columna de año para calcular la matrícula anual.")
        return table

    high = table.loc[table["records"].idxmax()]
    low = table.loc[table["records"].idxmin()]
    metric_cols = st.columns(2)
    metric_cols[0].metric("Año con mayor matrícula", f"{high['year']}", f"{int(high['records'])} registros")
    metric_cols[1].metric("Año con menor matrícula", f"{low['year']}", f"{int(low['records'])} registros")

    display_table = table.rename(columns={"year": "Año", "records": "Registros"})
    chart_data = prepare_line_chart(display_table, "Año", "Registros")
    st.line_chart(chart_data)
    safe_dataframe(display_table, use_container_width=True)

    st.subheader("Variación año a año")
    display_growth = growth.rename(
        columns={
            "year": "Año",
            "records": "Registros",
            "absolute_change": "Variación absoluta",
            "percent_change": "Variación porcentual",
        }
    )
    safe_dataframe(display_growth, use_container_width=True)
    return table


def display_enrollment_by_course(cleaned: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Render course-level analysis and return course table and matrix."""

    st.header("Matrícula por curso")
    course_table = enrollment_by_course(cleaned)
    matrix = year_course_matrix(cleaned)

    if course_table.empty:
        st.warning("No se detectó una columna de curso para calcular la matrícula por curso.")
        return course_table, matrix

    display_course = course_table.rename(columns={"course": "Curso", "records": "Registros"})
    chart_data = prepare_bar_chart(display_course, "Curso", "Registros")
    st.bar_chart(chart_data)
    safe_dataframe(display_course, use_container_width=True)

    percentages = course_percentages(course_table).rename(
        columns={"course": "Curso", "records": "Registros", "percent": "Porcentaje"}
    )
    st.subheader("Porcentajes por curso")
    safe_dataframe(percentages, use_container_width=True)

    st.subheader("Matriz año por curso")
    if matrix.empty:
        st.info("La matriz año por curso requiere columnas de año y curso.")
    else:
        try:
            styled_matrix = matrix.style.background_gradient(cmap="Blues", axis=None)
            safe_dataframe(styled_matrix, use_container_width=True)
        except (ImportError, ValueError, AttributeError):
            # Fallback when Styler rendering fails (e.g., missing matplotlib on Streamlit Cloud)
            safe_dataframe(matrix, use_container_width=True)

    return course_table, matrix


def display_age_analysis(cleaned: pd.DataFrame) -> pd.DataFrame:
    """Render age analysis and return the age summary table."""

    st.header("Análisis de edad")
    if "age" not in cleaned.columns:
        st.info("No se detectó una columna de edad. Esta sección queda disponible cuando el archivo incluye edad.")
        return pd.DataFrame()

    summary = age_summary(cleaned)
    if summary.empty:
        st.info("La columna de edad no contiene valores numéricos suficientes para analizar.")
        return summary

    metrics = {row.metric: row.value for row in summary.itertuples()}
    metric_cols = st.columns(5)
    metric_cols[0].metric("Media", metrics.get("media", "Sin dato"))
    metric_cols[1].metric("Mediana", metrics.get("mediana", "Sin dato"))
    metric_cols[2].metric("Mínimo", metrics.get("minimo", "Sin dato"))
    metric_cols[3].metric("Máximo", metrics.get("maximo", "Sin dato"))
    metric_cols[4].metric("Desv. estándar", metrics.get("desviacion_estandar", "Sin dato"))

    age_distribution = prepare_age_distribution(cleaned)
    if not age_distribution.empty:
        display_age_distribution = age_distribution.rename(columns={"age": "Edad", "records": "Registros"})
        st.bar_chart(display_age_distribution.set_index("Edad"))

    year_col = detect_year_column(cleaned)
    course_col = detect_course_column(cleaned)
    tab_ranges, tab_year, tab_course, tab_outliers = st.tabs(
        ["Rangos etarios", "Edad por año", "Edad por curso", "Valores atípicos"]
    )
    with tab_ranges:
        display_ranges = age_ranges(cleaned).rename(columns={"age_range": "Rango etario", "records": "Registros"})
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
                .rename(columns={year_col: "Año", "age": "Edad promedio"})
            )
            safe_dataframe(by_year, use_container_width=True)
        else:
            st.info("No se detectó columna de año.")
    with tab_course:
        if course_col:
            by_course = (
                cleaned.assign(age=pd.to_numeric(cleaned["age"], errors="coerce"))
                .dropna(subset=["age", course_col])
                .groupby(course_col)["age"]
                .mean()
                .round(2)
                .reset_index()
                .rename(columns={course_col: "Curso", "age": "Edad promedio"})
            )
            safe_dataframe(by_course, use_container_width=True)
        else:
            st.info("No se detectó columna de curso.")
    with tab_outliers:
        age = pd.to_numeric(cleaned["age"], errors="coerce")
        quartile_1 = age.quantile(0.25)
        quartile_3 = age.quantile(0.75)
        iqr = quartile_3 - quartile_1
        lower = quartile_1 - 1.5 * iqr
        upper = quartile_3 + 1.5 * iqr
        outlier_count = int(((age < lower) | (age > upper)).sum())
        st.metric("Posibles valores atípicos en edad", outlier_count)
        st.caption(f"Criterio IQR aplicado: menor que {lower:.1f} o mayor que {upper:.1f}.")

    return summary


def display_categorical_analysis(cleaned: pd.DataFrame) -> pd.DataFrame:
    """Render categorical distributions and return a summary table."""

    st.header("Análisis categórico")
    categorical_report = categorical_summary(cleaned)
    valid_categorical_columns = get_valid_categorical_columns(cleaned)

    if not valid_categorical_columns:
        st.info("No se detectaron variables categóricas adecuadas para analizar.")
        return categorical_report

    selected_column = st.sidebar.selectbox("Columna categórica para explorar", valid_categorical_columns)
    
    # Build distribution table with normalized types
    distribution = (
        cleaned[selected_column]
        .fillna("Sin dato")
        .astype(str)
        .value_counts(dropna=False)
        .reset_index()
    )
    distribution.columns = ["Categoría", "Frecuencia"]
    distribution["Porcentaje"] = (
        (distribution["Frecuencia"] / distribution["Frecuencia"].sum() * 100).round(2)
    )
    distribution = distribution.reset_index(drop=True)

    st.subheader(f"Distribución de {selected_column}")
    if "Categoría" in distribution.columns and "Frecuencia" in distribution.columns:
        try:
            st.bar_chart(distribution.set_index("Categoría")["Frecuencia"])
        except (ValueError, TypeError):
            pass  # Chart may fail with certain types, but don't crash
    
    safe_dataframe(distribution, use_container_width=True)

    st.subheader("Resumen categórico")
    display_report = categorical_report.rename(
        columns={"column": "Columna", "value": "Valor", "records": "Registros"}
    )
    safe_dataframe(display_report, use_container_width=True)
    return categorical_report


def display_descriptive_statistics(cleaned: pd.DataFrame, missing_report: pd.DataFrame) -> None:
    """Render descriptive statistics section."""

    st.header("Estadística descriptiva")
    tab_numeric, tab_categorical, tab_missing, tab_cardinality = st.tabs(
        ["Variables numéricas", "Variables categóricas", "Valores faltantes", "Cardinalidad"]
    )
    with tab_numeric:
        numeric = numeric_summary(cleaned)
        if numeric.empty:
            st.info("No se detectaron variables numéricas.")
        else:
            safe_dataframe(numeric, use_container_width=True)
    with tab_categorical:
        categorical = categorical_summary(cleaned, max_unique=10)
        if categorical.empty:
            st.info("No se detectaron variables categóricas.")
        else:
            safe_dataframe(
                categorical.rename(columns={"column": "Columna", "value": "Valor", "records": "Registros"}),
                use_container_width=True,
            )
    with tab_missing:
        safe_dataframe(format_missing_table(missing_report), use_container_width=True)
    with tab_cardinality:
        cardinality = pd.DataFrame(
            {
                "Columna": cleaned.columns,
                "Valores únicos": [cleaned[column].nunique(dropna=True) for column in cleaned.columns],
            }
        )
        safe_dataframe(cardinality, use_container_width=True)


def display_crosstabs(cleaned: pd.DataFrame) -> dict[str, pd.DataFrame]:
    """Render available cross-tabulations and return them for export."""

    st.header("Cruces de variables")
    enriched = add_age_range_column(cleaned)
    year_col = detect_year_column(enriched)
    course_col = detect_course_column(enriched)
    available_crosstabs: dict[str, tuple[str, str]] = {}

    if year_col and course_col:
        available_crosstabs["Año por curso"] = (year_col, course_col)
    if year_col and "age_range" in enriched.columns:
        available_crosstabs["Año por rango etario"] = (year_col, "age_range")
    if course_col and "age_range" in enriched.columns:
        available_crosstabs["Curso por rango etario"] = (course_col, "age_range")
    if year_col and "gender_group" in enriched.columns:
        available_crosstabs["Año por género"] = (year_col, "gender_group")
    if course_col and "gender_group" in enriched.columns:
        available_crosstabs["Curso por género"] = (course_col, "gender_group")
    if year_col and "nationality_group" in enriched.columns:
        available_crosstabs["Año por nacionalidad"] = (year_col, "nationality_group")

    if not available_crosstabs:
        st.info("No hay suficientes columnas para generar cruces de variables.")
        return {}

    selected_tables = st.multiselect(
        "Seleccionar cruces para visualizar",
        options=list(available_crosstabs.keys()),
        default=list(available_crosstabs.keys())[:3],
    )
    rendered_tables: dict[str, pd.DataFrame] = {}
    for label in selected_tables:
        row_col, col_col = available_crosstabs[label]
        table = crosstab_summary(enriched, row_col, col_col)
        rendered_tables[label] = table
        st.subheader(label)
        safe_dataframe(table, use_container_width=True)
        st.download_button(
            f"Descargar {label.lower()}",
            data=make_csv_download(table.reset_index()),
            file_name=f"{label.lower().replace(' ', '_')}.csv",
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
) -> None:
    """Render download buttons for exportable outputs."""

    st.header("Exportaciones")
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
        "cleaned_dataset.csv": "Descargar dataset limpio",
        "enrollment_by_year.csv": "Descargar matrícula por año",
        "enrollment_by_course.csv": "Descargar matrícula por curso",
        "year_course_matrix.csv": "Descargar matriz año por curso",
        "missing_values_report.csv": "Descargar reporte de valores faltantes",
        "age_summary.csv": "Descargar resumen de edad",
        "categorical_summary.csv": "Descargar resumen categórico",
    }
    for index, (filename, table) in enumerate(tables.items()):
        export_columns[index % 2].download_button(
            labels.get(filename, f"Descargar {filename}"),
            data=make_csv_download(table),
            file_name=filename,
            mime="text/csv",
        )

    st.download_button(
        "Descargar resumen completo ZIP",
        data=build_zip_export(tables),
        file_name="full_analysis_summary.zip",
        mime="application/zip",
    )


def main() -> None:
    """Run the Streamlit app."""

    apply_page_styles()
    st.title("Analizador cuantitativo de matrícula escolar")
    st.markdown(
        "Aplicación interactiva para limpiar archivos institucionales, explorar matrícula por año y curso, "
        "analizar edades, generar cruces de variables y exportar resultados reproducibles."
    )
    st.markdown(
        '<div class="privacy-note">Esta aplicación procesa los archivos cargados en memoria y no almacena datos de estudiantes.</div>',
        unsafe_allow_html=True,
    )

    raw_data, source_label = load_input_data()
    if raw_data is None or raw_data.empty:
        st.info("Cargá un archivo o activá el dataset de ejemplo para iniciar el análisis.")
        return None

    st.sidebar.success(f"Datos cargados desde: {source_label}")

    with st.spinner("Limpiando y preparando datos..."):
        cleaned, metadata = clean_enrollment_dataset(raw_data)

    if cleaned.empty:
        st.warning("El dataset quedó vacío después de la limpieza.")
        return None

    missing_report = missing_values_summary(cleaned)
    display_general_eda(cleaned, metadata)
    enrollment_year = display_enrollment_by_year(cleaned)
    enrollment_course, matrix = display_enrollment_by_course(cleaned)
    age_report = display_age_analysis(cleaned)
    categorical_report = display_categorical_analysis(cleaned)
    display_descriptive_statistics(cleaned, missing_report)
    display_crosstabs(cleaned)

    st.header("Resumen automático")
    st.write(automatic_summary(cleaned))

    display_exports(
        cleaned=cleaned,
        enrollment_year=enrollment_year,
        enrollment_course=enrollment_course,
        matrix=matrix,
        missing_report=missing_report,
        age_report=age_report,
        categorical_report=categorical_report,
    )
    return None


if __name__ == "__main__":
    main()

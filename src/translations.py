"""Small translation layer for the Streamlit interface."""

from __future__ import annotations

from collections.abc import Mapping

import pandas as pd


DEFAULT_LANGUAGE = "es"
SUPPORTED_LANGUAGES = ("es", "en")


TRANSLATIONS: dict[str, dict[str, str]] = {
    "es": {
        "app_title": "Analizador cuantitativo de matrícula escolar",
        "app_description": (
            "Aplicación interactiva para limpiar archivos institucionales, explorar matrícula por año y curso, "
            "analizar edades, generar cruces de variables y exportar resultados reproducibles."
        ),
        "privacy_note": "Esta aplicación procesa los archivos cargados en memoria y no almacena datos de estudiantes.",
        "sidebar_language": "Idioma",
        "language_es": "Español",
        "language_en": "English",
        "sidebar_upload_header": "Carga de archivos",
        "sidebar_upload_caption": "Subí archivos CSV o Excel, o usá el dataset sintético incluido.",
        "upload_files": "Cargar archivos",
        "upload_help": "Los archivos se procesan en memoria durante la sesión.",
        "use_sample": "Usar dataset de ejemplo",
        "read_all_sheets": "Leer todas las hojas de Excel",
        "select_sheet": "Seleccionar hoja",
        "excel_sheet_error": "No se pudieron leer las hojas del Excel: {error}",
        "load_files_error": "No se pudieron cargar los archivos: {error}",
        "source_uploaded_files": "archivos cargados",
        "source_sample_dataset": "dataset sintético de ejemplo",
        "source_no_data": "sin datos",
        "source_error": "error",
        "general_eda": "Exploración general de datos",
        "total_records": "Total de registros",
        "column_count": "Cantidad de columnas",
        "detected_years": "Años detectados",
        "detected_courses": "Cursos detectados",
        "duplicate_student_ids": "Duplicados detectados en student_id: {count}",
        "dropped_empty_columns": "Columnas vacías eliminadas: {columns}",
        "no_empty_columns": "No se detectaron columnas completamente vacías.",
        "tab_preview": "Vista previa",
        "tab_missing": "Valores faltantes",
        "tab_types": "Tipos de datos",
        "enrollment_by_year": "Matrícula por año",
        "no_year_column": "No se detectó una columna de año para calcular la matrícula anual.",
        "highest_enrollment_year": "Año con mayor matrícula",
        "lowest_enrollment_year": "Año con menor matrícula",
        "records_delta": "{count} registros",
        "year_over_year_change": "Variación año a año",
        "enrollment_by_course": "Matrícula por curso",
        "no_course_column": "No se detectó una columna de curso para calcular la matrícula por curso.",
        "course_percentages": "Porcentajes por curso",
        "year_course_matrix": "Matriz año por curso",
        "year_course_matrix_requires_columns": "La matriz año por curso requiere columnas de año y curso.",
        "age_analysis": "Análisis de edad",
        "no_age_column": "No se detectó una columna de edad. Esta sección queda disponible cuando el archivo incluye edad.",
        "age_not_numeric": "La columna de edad no contiene valores numéricos suficientes para analizar.",
        "mean": "Media",
        "median": "Mediana",
        "minimum": "Mínimo",
        "maximum": "Máximo",
        "std_dev": "Desv. estándar",
        "no_data": "Sin dato",
        "age_ranges": "Rangos etarios",
        "age_by_year": "Edad por año",
        "age_by_course": "Edad por curso",
        "outliers": "Valores atípicos",
        "possible_age_outliers": "Posibles valores atípicos en edad",
        "iqr_caption": "Criterio IQR aplicado: menor que {lower:.1f} o mayor que {upper:.1f}.",
        "categorical_analysis": "Análisis categórico",
        "no_categorical_variables": "No se detectaron variables categóricas adecuadas para analizar.",
        "categorical_column_select": "Columna categórica para explorar",
        "distribution_of": "Distribución de {column}",
        "categorical_summary": "Resumen categórico",
        "descriptive_statistics": "Estadística descriptiva",
        "numeric_variables": "Variables numéricas",
        "categorical_variables": "Variables categóricas",
        "cardinality": "Cardinalidad",
        "no_numeric_variables": "No se detectaron variables numéricas.",
        "crosstabs": "Cruces de variables",
        "no_crosstabs": "No hay suficientes columnas para generar cruces de variables.",
        "select_crosstabs": "Seleccionar cruces para visualizar",
        "download_crosstab": "Descargar {label}",
        "exports": "Exportaciones",
        "download_cleaned_dataset": "Descargar dataset limpio",
        "download_enrollment_by_year": "Descargar matrícula por año",
        "download_enrollment_by_course": "Descargar matrícula por curso",
        "download_year_course_matrix": "Descargar matriz año por curso",
        "download_missing_values": "Descargar reporte de valores faltantes",
        "download_age_summary": "Descargar resumen de edad",
        "download_categorical_summary": "Descargar resumen categórico",
        "download_file": "Descargar {filename}",
        "download_zip": "Descargar resumen completo ZIP",
        "empty_start": "Cargá un archivo o activá el dataset de ejemplo para iniciar el análisis.",
        "loaded_source": "Datos cargados desde: {source}",
        "cleaning_spinner": "Limpiando y preparando datos...",
        "empty_after_cleaning": "El dataset quedó vacío después de la limpieza.",
        "automatic_summary": "Resumen automático",
        "summary_dataset": "El dataset procesado contiene {rows} registros y {columns} columnas.",
        "summary_period": "Cubre el período {min_year} a {max_year}.",
        "summary_highest_year": "El año con mayor matrícula es {year} con {records} registros.",
        "summary_lowest_year": "El año con menor matrícula es {year} con {records} registros.",
        "summary_no_year": "No se detectó una columna de año suficiente para calcular evolución anual.",
        "summary_top_course": "El curso más frecuente es {course} con {records} registros.",
        "summary_no_course": "No se detectó una columna de curso suficiente para calcular distribución por curso.",
        "summary_average_age": "La edad promedio registrada es {age:.1f} años.",
        "summary_missing": "Las columnas con más valores faltantes son: {columns}.",
        "summary_no_missing": "No se detectaron valores faltantes en las columnas procesadas.",
    },
    "en": {
        "app_title": "School Enrollment Quantitative Analyzer",
        "app_description": (
            "Interactive app for cleaning institutional files, exploring enrollment by year and course, "
            "analyzing ages, generating cross-tabulations, and exporting reproducible outputs."
        ),
        "privacy_note": "This app processes uploaded files in memory and does not store student data.",
        "sidebar_language": "Language",
        "language_es": "Español",
        "language_en": "English",
        "sidebar_upload_header": "File upload",
        "sidebar_upload_caption": "Upload CSV or Excel files, or use the included synthetic dataset.",
        "upload_files": "Upload files",
        "upload_help": "Files are processed in memory during the session.",
        "use_sample": "Use sample dataset",
        "read_all_sheets": "Read all Excel sheets",
        "select_sheet": "Select sheet",
        "excel_sheet_error": "Could not read the Excel sheets: {error}",
        "load_files_error": "Could not load the files: {error}",
        "source_uploaded_files": "uploaded files",
        "source_sample_dataset": "synthetic sample dataset",
        "source_no_data": "no data",
        "source_error": "error",
        "general_eda": "General data exploration",
        "total_records": "Total records",
        "column_count": "Number of columns",
        "detected_years": "Detected years",
        "detected_courses": "Detected courses",
        "duplicate_student_ids": "Duplicates detected in student_id: {count}",
        "dropped_empty_columns": "Empty columns removed: {columns}",
        "no_empty_columns": "No completely empty columns were detected.",
        "tab_preview": "Preview",
        "tab_missing": "Missing values",
        "tab_types": "Data types",
        "enrollment_by_year": "Enrollment by year",
        "no_year_column": "No year column was detected to calculate annual enrollment.",
        "highest_enrollment_year": "Year with highest enrollment",
        "lowest_enrollment_year": "Year with lowest enrollment",
        "records_delta": "{count} records",
        "year_over_year_change": "Year-over-year change",
        "enrollment_by_course": "Enrollment by course",
        "no_course_column": "No course column was detected to calculate enrollment by course.",
        "course_percentages": "Course percentages",
        "year_course_matrix": "Year-course matrix",
        "year_course_matrix_requires_columns": "The year-course matrix requires year and course columns.",
        "age_analysis": "Age analysis",
        "no_age_column": "No age column was detected. This section becomes available when the file includes age.",
        "age_not_numeric": "The age column does not contain enough numeric values to analyze.",
        "mean": "Mean",
        "median": "Median",
        "minimum": "Minimum",
        "maximum": "Maximum",
        "std_dev": "Std. deviation",
        "no_data": "No data",
        "age_ranges": "Age ranges",
        "age_by_year": "Age by year",
        "age_by_course": "Age by course",
        "outliers": "Outliers",
        "possible_age_outliers": "Possible age outliers",
        "iqr_caption": "IQR rule applied: lower than {lower:.1f} or higher than {upper:.1f}.",
        "categorical_analysis": "Categorical analysis",
        "no_categorical_variables": "No suitable categorical variables were detected for analysis.",
        "categorical_column_select": "Categorical column to explore",
        "distribution_of": "Distribution of {column}",
        "categorical_summary": "Categorical summary",
        "descriptive_statistics": "Descriptive statistics",
        "numeric_variables": "Numeric variables",
        "categorical_variables": "Categorical variables",
        "cardinality": "Cardinality",
        "no_numeric_variables": "No numeric variables were detected.",
        "crosstabs": "Cross-tabulations",
        "no_crosstabs": "There are not enough columns to generate cross-tabulations.",
        "select_crosstabs": "Select cross-tabulations to display",
        "download_crosstab": "Download {label}",
        "exports": "Exports",
        "download_cleaned_dataset": "Download cleaned dataset",
        "download_enrollment_by_year": "Download enrollment by year",
        "download_enrollment_by_course": "Download enrollment by course",
        "download_year_course_matrix": "Download year-course matrix",
        "download_missing_values": "Download missing values report",
        "download_age_summary": "Download age summary",
        "download_categorical_summary": "Download categorical summary",
        "download_file": "Download {filename}",
        "download_zip": "Download full ZIP summary",
        "empty_start": "Upload a file or enable the sample dataset to start the analysis.",
        "loaded_source": "Data loaded from: {source}",
        "cleaning_spinner": "Cleaning and preparing data...",
        "empty_after_cleaning": "The dataset is empty after cleaning.",
        "automatic_summary": "Automatic summary",
        "summary_dataset": "The processed dataset contains {rows} records and {columns} columns.",
        "summary_period": "It covers the period from {min_year} to {max_year}.",
        "summary_highest_year": "The year with the highest enrollment is {year}, with {records} records.",
        "summary_lowest_year": "The year with the lowest enrollment is {year}, with {records} records.",
        "summary_no_year": "No sufficient year column was detected to calculate annual trends.",
        "summary_top_course": "The most frequent course is {course}, with {records} records.",
        "summary_no_course": "No sufficient course column was detected to calculate course distribution.",
        "summary_average_age": "The recorded average age is {age:.1f} years.",
        "summary_missing": "The columns with the most missing values are: {columns}.",
        "summary_no_missing": "No missing values were detected in the processed columns.",
    },
}


COLUMN_LABELS: dict[str, dict[str, str]] = {
    "es": {
        "year": "Año",
        "records": "Registros",
        "course": "Curso",
        "age": "Edad",
        "age_range": "Rango etario",
        "student_id": "ID estudiante",
        "gender_group": "Grupo de género",
        "nationality_group": "Grupo de nacionalidad",
        "enrollment_status": "Estado de matrícula",
        "neighborhood_group": "Zona o barrio",
        "column": "Columna",
        "missing_count": "Valores faltantes",
        "missing_percent": "Porcentaje faltante",
        "value": "Valor",
        "metric": "Métrica",
        "percent": "Porcentaje",
        "absolute_change": "Variación absoluta",
        "percent_change": "Variación porcentual",
        "count": "Conteo",
        "mean": "Media",
        "std": "Desv. estándar",
        "min": "Mínimo",
        "25%": "25%",
        "50%": "50%",
        "75%": "75%",
        "max": "Máximo",
        "unique_values": "Valores únicos",
        "average_age": "Edad promedio",
        "category": "Categoría",
        "frequency": "Frecuencia",
    },
    "en": {
        "year": "Year",
        "records": "Records",
        "course": "Course",
        "age": "Age",
        "age_range": "Age range",
        "student_id": "Student ID",
        "gender_group": "Gender group",
        "nationality_group": "Nationality group",
        "enrollment_status": "Enrollment status",
        "neighborhood_group": "Neighborhood group",
        "column": "Column",
        "missing_count": "Missing values",
        "missing_percent": "Missing percent",
        "value": "Value",
        "metric": "Metric",
        "percent": "Percent",
        "absolute_change": "Absolute change",
        "percent_change": "Percent change",
        "count": "Count",
        "mean": "Mean",
        "std": "Std. deviation",
        "min": "Minimum",
        "25%": "25%",
        "50%": "50%",
        "75%": "75%",
        "max": "Maximum",
        "unique_values": "Unique values",
        "average_age": "Average age",
        "category": "Category",
        "frequency": "Frequency",
    },
}


AGE_METRIC_LABELS: dict[str, dict[str, str]] = {
    "es": {
        "media": "Media",
        "mediana": "Mediana",
        "minimo": "Mínimo",
        "maximo": "Máximo",
        "desviacion_estandar": "Desv. estándar",
    },
    "en": {
        "media": "Mean",
        "mediana": "Median",
        "minimo": "Minimum",
        "maximo": "Maximum",
        "desviacion_estandar": "Std. deviation",
    },
}


AGE_RANGE_LABELS: dict[str, dict[str, str]] = {
    "es": {
        "menor_15": "Menor de 15",
        "15_17": "15 a 17",
        "18_20": "18 a 20",
        "21_25": "21 a 25",
        "mayor_25": "Mayor de 25",
        "sin_dato": "Sin dato",
    },
    "en": {
        "menor_15": "Under 15",
        "15_17": "15 to 17",
        "18_20": "18 to 20",
        "21_25": "21 to 25",
        "mayor_25": "Over 25",
        "sin_dato": "No data",
    },
}


CROSSTAB_LABELS: dict[str, dict[str, str]] = {
    "es": {
        "year_course": "Año por curso",
        "year_age_range": "Año por rango etario",
        "course_age_range": "Curso por rango etario",
        "year_gender": "Año por género",
        "course_gender": "Curso por género",
        "year_nationality": "Año por nacionalidad",
    },
    "en": {
        "year_course": "Year by course",
        "year_age_range": "Year by age range",
        "course_age_range": "Course by age range",
        "year_gender": "Year by gender",
        "course_gender": "Course by gender",
        "year_nationality": "Year by nationality",
    },
}


def normalize_language(lang: str | None) -> str:
    """Return a supported language code."""

    return lang if lang in SUPPORTED_LANGUAGES else DEFAULT_LANGUAGE


def t(key: str, lang: str = DEFAULT_LANGUAGE, **kwargs: object) -> str:
    """Translate a UI key with Spanish fallback."""

    language = normalize_language(lang)
    template = TRANSLATIONS.get(language, TRANSLATIONS[DEFAULT_LANGUAGE]).get(
        key, TRANSLATIONS[DEFAULT_LANGUAGE].get(key, key)
    )
    if kwargs:
        return template.format(**kwargs)
    return template


def label_column(column: object, lang: str = DEFAULT_LANGUAGE) -> str:
    """Return a translated display label for a column name."""

    language = normalize_language(lang)
    column_key = str(column)
    return COLUMN_LABELS.get(language, COLUMN_LABELS[DEFAULT_LANGUAGE]).get(column_key, column_key)


def label_columns(df: pd.DataFrame, lang: str = DEFAULT_LANGUAGE) -> pd.DataFrame:
    """Return a copy with translated display column names."""

    return df.rename(columns={column: label_column(column, lang) for column in df.columns})


def label_age_metric(metric: object, lang: str = DEFAULT_LANGUAGE) -> str:
    """Return a translated display label for an age metric key."""

    language = normalize_language(lang)
    metric_key = str(metric)
    return AGE_METRIC_LABELS.get(language, AGE_METRIC_LABELS[DEFAULT_LANGUAGE]).get(metric_key, metric_key)


def label_age_range(value: object, lang: str = DEFAULT_LANGUAGE) -> str:
    """Return a translated display label for an age-range key."""

    language = normalize_language(lang)
    value_key = str(value)
    return AGE_RANGE_LABELS.get(language, AGE_RANGE_LABELS[DEFAULT_LANGUAGE]).get(value_key, value_key)


def label_crosstab(key: str, lang: str = DEFAULT_LANGUAGE) -> str:
    """Return a translated display label for a crosstab key."""

    language = normalize_language(lang)
    return CROSSTAB_LABELS.get(language, CROSSTAB_LABELS[DEFAULT_LANGUAGE]).get(key, key)


def label_crosstab_options(options: Mapping[str, tuple[str, str]], lang: str = DEFAULT_LANGUAGE) -> dict[str, str]:
    """Return translated labels for available crosstab option keys."""

    return {key: label_crosstab(key, lang) for key in options}

# School Enrollment Quantitative Analyzer

Streamlit application for interactive quantitative analysis of school enrollment data. The app is designed as a privacy-safe portfolio project inspired by a quantitative educational analysis notebook, with file upload, basic cleaning, exploratory analysis, descriptive statistics, enrollment summaries, cross-tabulations, visual indicators, and exportable outputs.

The Streamlit app supports English and Spanish through a sidebar language selector.

Esta app de Streamlit permite alternar entre español e inglés desde la barra lateral.

## Live app

Streamlit app: [https://school-enrollment-quantitative-analyzer-e27746dqfudiegt27szbez.streamlit.app/](https://school-enrollment-quantitative-analyzer-e27746dqfudiegt27szbez.streamlit.app/)

## Objective

This project helps transform institutional enrollment spreadsheets into clear, reproducible quantitative outputs. It supports CSV and Excel uploads, detects common enrollment columns, cleans basic formatting issues, summarizes enrollment by year and course, analyzes age distributions, and exports cleaned data and analysis tables.

## Features

- Upload one or more CSV or Excel files.
- Read a selected Excel sheet or combine all sheets.
- Use a built-in synthetic sample dataset.
- Normalize column names, remove accents, trim extra spaces, and drop empty columns.
- Detect common enrollment columns such as year, course, age, student ID, gender, nationality, status, and neighborhood groups.
- Show general EDA, missing values, data types, duplicates, and preview tables.
- Analyze enrollment by year, course, year-course matrix, age ranges, and categorical variables.
- Generate simple cross-tabulations such as year by course, course by age range, and year by gender.
- Export cleaned data and analysis tables as CSV files.
- Export a ZIP archive with the main outputs.
- Switch the interface between Spanish and English without duplicating the app.
- Run automated tests with pytest and GitHub Actions.

## Technical stack

Python · Streamlit · pandas · NumPy · openpyxl · pytest · GitHub Actions

## Repository structure

```text
school-enrollment-quantitative-analyzer/
├── app.py
├── README.md
├── requirements.txt
├── pytest.ini
├── .github/
│   └── workflows/
│       └── tests.yml
├── .streamlit/
│   └── config.toml
├── data/
│   └── sample_enrollment_data.csv
├── src/
│   ├── __init__.py
│   ├── io_utils.py
│   ├── data_cleaning.py
│   ├── enrollment_analysis.py
│   ├── eda.py
│   ├── translations.py
│   ├── visualization.py
│   └── export_utils.py
└── tests/
    ├── test_data_cleaning.py
    ├── test_enrollment_analysis.py
    ├── test_eda.py
    └── test_translations.py
```

## Run locally

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

## Run tests

```bash
pytest -q
python -m compileall .
```

## Uploading files

The app accepts `.csv`, `.xlsx`, and `.xls` files. Excel files can be read from one selected sheet or combined across all sheets. Uploaded files are processed in memory during the Streamlit session.

Expected columns are flexible. The app attempts to map common Spanish and English names to canonical internal fields, including:

- `year` / `año` / `anio_libro`
- `course` / `curso` / `curso_ingreso`
- `age` / `edad`
- `student_id` / `id_estudiante`
- `gender` / `sexo` / `genero`
- `nationality` / `nacionalidad`
- `enrollment_status` / `estado`
- `neighborhood` / `barrio`

## Privacy note

This repository does not contain real student data. The included sample dataset is fully synthetic and exists only to demonstrate the workflow. Uploaded files are processed in memory and are not stored by the application.

## Deployment

The public demo is deployed on Streamlit Cloud:
[https://school-enrollment-quantitative-analyzer-e27746dqfudiegt27szbez.streamlit.app/](https://school-enrollment-quantitative-analyzer-e27746dqfudiegt27szbez.streamlit.app/)

## Portfolio connection

This project complements a professional portfolio focused on AI evaluation, STEM reasoning review, Python data workflows, educational analytics, reproducible reporting, and privacy-safe public demos.

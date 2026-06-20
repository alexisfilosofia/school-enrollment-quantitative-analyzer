from src.translations import TRANSLATIONS, label_column, t


def test_basic_translation_keys_exist_for_supported_languages():
    required_keys = {"app_title", "sidebar_language", "upload_files", "exports"}

    assert required_keys.issubset(TRANSLATIONS["es"])
    assert required_keys.issubset(TRANSLATIONS["en"])


def test_app_title_translates_to_spanish_and_english():
    assert t("app_title", "es") == "Analizador cuantitativo de matrícula escolar"
    assert t("app_title", "en") == "School Enrollment Quantitative Analyzer"


def test_translation_fallbacks():
    assert t("app_title", "unknown") == "Analizador cuantitativo de matrícula escolar"
    assert t("missing_key", "en") == "missing_key"


def test_column_label_translation():
    assert label_column("year", "es") == "Año"
    assert label_column("year", "en") == "Year"
    assert label_column("custom_column", "en") == "custom_column"

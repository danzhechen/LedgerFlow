from veritas_accounting.utils.sheets import default_sheets_to_process, detect_year_like_sheets


def test_detect_year_like_sheets_sorts_and_filters() -> None:
    sheets = ["README", "2024", "2022", "Sheet1", "2023"]
    assert detect_year_like_sheets(sheets) == ["2022", "2023", "2024"]


def test_default_sheets_to_process_prefers_year_sheets() -> None:
    sheets = ["Sheet1", "2024", "Notes", "2022"]
    assert default_sheets_to_process(sheets) == ["2022", "2024"]


def test_default_sheets_to_process_falls_back_to_all() -> None:
    sheets = ["Sheet1", "Sheet2"]
    assert default_sheets_to_process(sheets) == ["Sheet1", "Sheet2"]


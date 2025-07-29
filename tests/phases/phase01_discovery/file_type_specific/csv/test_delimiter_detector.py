import pytest
from src.phases.phase01_discovery.file_type_specific.csv.delimiter_detector import detect_csv_delimiter

@pytest.fixture
def csv_file_semicolon(tmp_path):
    file = tmp_path / "test_semicolon.csv"
    file.write_text("h1;h2\nv1;v2")
    return str(file)

@pytest.fixture
def csv_file_comma(tmp_path):
    file = tmp_path / "test_comma.csv"
    file.write_text("h1,h2\nv1,v2")
    return str(file)

def test_detect_csv_delimiter_semicolon(csv_file_semicolon):
    result = detect_csv_delimiter(csv_file_semicolon)
    assert result['delimiter'] == ';'

def test_detect_csv_delimiter_comma(csv_file_comma):
    result = detect_csv_delimiter(csv_file_comma)
    assert result['delimiter'] == ','

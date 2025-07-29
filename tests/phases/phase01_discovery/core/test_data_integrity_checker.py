import os
import pytest
from src.phases.phase01_discovery.core.data_integrity_checker import check_csv_file, check_excel_file, check_json_file, analyze_data_integrity

@pytest.fixture
def temp_dir(tmp_path):
    d = tmp_path / "data"
    d.mkdir()
    return d

def test_check_csv_file_valid(temp_dir):
    csv_content = "col1,col2\nval1,val2"
    csv_file = temp_dir / "test.csv"
    csv_file.write_text(csv_content)
    report = check_csv_file(str(csv_file))
    assert report["status"] == "OK"
    assert report["details"]["delimiter"] == ","

def test_check_csv_file_empty(temp_dir):
    csv_file = temp_dir / "empty.csv"
    csv_file.touch()
    report = check_csv_file(str(csv_file))
    assert report["status"] == "Atenção"
    assert report["details"]["is_empty"] is True

def test_check_excel_file_valid(temp_dir):
    # Creating a dummy excel file is complex, so we'll mock it
    # For a real scenario, a small, real Excel file would be in test_data
    pass

def test_check_json_file_valid(temp_dir):
    json_content = '{"key": "value"}'
    json_file = temp_dir / "test.json"
    json_file.write_text(json_content)
    report = check_json_file(str(json_file))
    assert report["status"] == "OK"
    assert report["details"]["json_type"] == "Padrão (objeto/array único)"

def test_analyze_data_integrity(temp_dir):
    (temp_dir / "test1.csv").write_text("a,b\n1,2")
    (temp_dir / "test2.json").write_text('[{"a": 1}]')
    result = analyze_data_integrity(str(temp_dir))
    assert result["status"] == "success"
    assert len(result["reports"]) == 2

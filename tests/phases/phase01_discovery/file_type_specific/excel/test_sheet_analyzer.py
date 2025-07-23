import os
import pandas as pd
import pytest
from src.phases.phase01_discovery.file_type_specific.excel.sheet_analyzer import analyze_excel_sheets

@pytest.fixture
def sample_excel_file(tmp_path):
    """Create a sample Excel file for testing."""
    file_path = tmp_path / "test_excel.xlsx"
    with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
        pd.DataFrame({"A": [1, 2], "B": [3, 4]}).to_excel(writer, sheet_name="Sheet1", index=False)
        pd.DataFrame({"X": [5, 6], "Y": [7, 8], "Z": [9, 10]}).to_excel(writer, sheet_name="Sheet2", index=False)
    return str(file_path)

@pytest.fixture
def empty_excel_file(tmp_path):
    """Create an empty Excel file."""
    file_path = tmp_path / "empty_excel.xlsx"
    with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
        pass
    return str(file_path)

@pytest.fixture
def corrupted_excel_file(tmp_path):
    """Create a corrupted (non-Excel) file with an .xlsx extension."""
    file_path = tmp_path / "corrupted.xlsx"
    with open(file_path, "w") as f:
        f.write("this is not an excel file")
    return str(file_path)


def test_analyze_excel_sheets_success(sample_excel_file):
    """Test successful analysis of a valid Excel file."""
    result = analyze_excel_sheets(sample_excel_file)

    assert result["status"] == "success"
    assert result["num_sheets"] == 2
    assert len(result["sheets_info"]) == 2

    sheet1_info = result["sheets_info"][0]
    assert sheet1_info["sheet_name"] == "Sheet1"
    assert sheet1_info["is_readable"] is True
    assert sheet1_info["num_columns"] == 2
    assert sheet1_info["error_message"] is None

    sheet2_info = result["sheets_info"][1]
    assert sheet2_info["sheet_name"] == "Sheet2"
    assert sheet2_info["is_readable"] is True
    assert sheet2_info["num_columns"] == 3
    assert sheet2_info["error_message"] is None

def test_analyze_excel_sheets_empty_file(empty_excel_file):
    """Test analysis of an empty Excel file."""
    result = analyze_excel_sheets(empty_excel_file)

    assert result["status"] == "success"
    assert result["num_sheets"] == 0
    assert len(result["sheets_info"]) == 0

def test_analyze_excel_sheets_corrupted_file(corrupted_excel_file):
    """Test analysis of a corrupted Excel file."""
    result = analyze_excel_sheets(corrupted_excel_file)

    assert result["status"] == "error"
    assert "error_message" in result
    assert result["num_sheets"] == 0
    assert len(result["sheets_info"]) == 0

def test_analyze_excel_sheets_nonexistent_file():
    """Test analysis of a nonexistent file."""
    result = analyze_excel_sheets("nonexistent_file.xlsx")

    assert result["status"] == "error"
    assert "error_message" in result
    assert "No such file or directory" in result["error_message"]
    assert result["num_sheets"] == 0
    assert len(result["sheets_info"]) == 0

import os
import pytest
from src.phases.phase01_discovery.file_type_specific.csv.column_consistency_checker import check_csv_structures

@pytest.fixture
def csv_files(tmp_path):
    d = tmp_path / "data"
    d.mkdir()
    (d / "file1.csv").write_text("h1,h2\nv1,v2")
    (d / "file2.csv").write_text("h1,h2\nv3,v4")
    (d / "file3_inconsistent.csv").write_text("h1,h3\nv5,v6")
    return str(d)

from pathlib import Path

def test_check_csv_structures_consistent(csv_files):
    csv_path = Path(csv_files)
    # Create a temporary file that is consistent
    (csv_path / "file2_consistent.csv").write_text("h1,h2\nv3,v4")

    # Remove inconsistent file for this test
    os.remove(csv_path / "file3_inconsistent.csv")
    os.remove(csv_path / "file2.csv") # remove the original file2.csv as well

    result = check_csv_structures(str(csv_path), detected_delimiters_map={
        str(csv_path / "file1.csv"): ",",
        str(csv_path / "file2_consistent.csv"): ","
    })

    assert result['status'] == 'success'
    assert len(result['results']) == 2
    assert result['results'][0]['status'] == 'Referência'
    assert result['results'][1]['status'] == 'OK'

def test_check_csv_structures_inconsistent(csv_files):
    result = check_csv_structures(csv_files, detected_delimiters_map={
        os.path.join(csv_files, "file1.csv"): ",",
        os.path.join(csv_files, "file2.csv"): ",",
        os.path.join(csv_files, "file3_inconsistent.csv"): ","
    })
    assert result['status'] == 'success'
    assert len(result['results']) == 3
    assert any(r['status'] == 'Inconsistente' for r in result['results'])

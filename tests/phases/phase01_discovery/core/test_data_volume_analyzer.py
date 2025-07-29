import os
import pytest
from src.phases.phase01_discovery.core.data_volume_analyzer import get_file_metrics, analyze_data_volume

@pytest.fixture
def temp_files(tmp_path):
    d = tmp_path / "data"
    d.mkdir()
    (d / "test1.csv").write_text("a,b\n1,2\n3,4")
    (d / "test2.csv").write_text("a,b,c\n1,2,3")
    return [str(d / "test1.csv"), str(d / "test2.csv")]

def test_get_file_metrics(temp_files):
    metrics = get_file_metrics(temp_files[0], delimiter=',')
    assert metrics['registros'] == 2
    assert metrics['tamanho_bytes'] > 0

def test_analyze_data_volume(temp_files):
    analysis = analyze_data_volume(temp_files, delimiter=',')
    assert analysis['overall_summary']['total_registros_geral'] == 3
    assert len(analysis['summary_by_extension']) == 1
    assert analysis['summary_by_extension'][0]['extensao'] == 'csv'

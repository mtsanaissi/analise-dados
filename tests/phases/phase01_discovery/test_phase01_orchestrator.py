from pathlib import Path
import os
import json
import pytest
from src.phases.phase01_discovery.phase01_orchestrator import run_discovery_phase


@pytest.fixture
def project_dir(tmp_path):
    d = tmp_path / "project"
    d.mkdir()
    (d / "data.csv").write_text("id,name\n1,test")
    (d / "schema.json").write_text('{"key": "value"}')
    return str(d)


def test_run_discovery_phase(project_dir):
    # We pass an empty list for extra_args to use default behavior
    results_wrapper = run_discovery_phase(project_dir, [])

    assert results_wrapper['status'] == 'success'
    assert 'detailed_results' in results_wrapper
    detailed_results = results_wrapper['detailed_results']

    # Check if all analysis types are present
    assert "encoding_analysis" in detailed_results
    assert "data_volume_analysis" in detailed_results
    assert "data_integrity_analysis" in detailed_results
    assert "csv_delimiter_analysis" in detailed_results
    assert "csv_column_consistency_analysis" in detailed_results
    assert "json_schema_validation" in detailed_results

    # Check if the report was generated
    report_path = os.path.join(project_dir, "fad-metadados", "discovery_report.json")
    assert os.path.exists(report_path)

    with open(report_path, 'r') as f:
        report_data = json.load(f)
    assert report_data['status'] == 'success'


def test_run_discovery_phase_compare_fields(project_dir):
    project_path = Path(project_dir)
    # Add another CSV with a different structure
    (project_path / "data2.csv").write_text("id,age\n2,30")

    # Pass '--compare-fields' to enable the feature
    results_wrapper = run_discovery_phase(
        str(project_path), ['--compare-fields'])

    assert results_wrapper['status'] == 'success'
    detailed_results = results_wrapper['detailed_results']

    # Check that field comparison analysis was performed
    assert "field_comparison_analysis" in detailed_results
    assert len(detailed_results['field_comparison_analysis']) > 0

    # Find the comparison result for the second CSV in the correct analysis
    comparison = next(
        (item for item in detailed_results['csv_column_consistency_analysis'] if item['file'] == 'data2.csv'), None)
    assert comparison is not None
    assert comparison['status'] == 'Inconsistente'
    assert 'details' in comparison
    assert "Diferença na coluna 2" in comparison['details']['message']

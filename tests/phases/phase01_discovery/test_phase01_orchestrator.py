from pathlib import Path
import os
import json
import pytest
from src.phases.phase01_discovery.phase01_orchestrator import run_discovery_logic


@pytest.fixture
def project_dir(tmp_path):
    d = tmp_path / "project"
    d.mkdir()
    (d / "data.csv").write_text("id,name\n1,test")
    (d / "schema.json").write_text('{"key": "value"}')
    return str(d)


def test_run_discovery_logic_success(project_dir):
    """
    Testa a execução bem-sucedida de run_discovery_logic com parâmetros padrão.
    Valida se o relatório é gerado e o dicionário de retorno está correto.
    """
    result = run_discovery_logic(data_project_path=project_dir)

    assert result['status'] == 'success'
    assert "Fase de Descoberta e Diagnóstico concluída com sucesso" in result['message']
    assert result['report_path'] is not None
    assert os.path.exists(result['report_path'])

    report_path = os.path.join(
        project_dir, "fad-metadados", "discovery_report.json")
    assert result['report_path'] == report_path

    with open(report_path, 'r') as f:
        report_data = json.load(f)
    assert report_data['status'] == 'success'
    assert "detailed_results" in report_data


def test_run_discovery_logic_compare_fields(project_dir):
    """
    Testa a funcionalidade de comparação de campos, validando se a análise
    é executada e se as inconsistências são corretamente identificadas.
    """
    project_path = Path(project_dir)
    (project_path / "data2.csv").write_text("id,age\n2,30")

    result = run_discovery_logic(
        data_project_path=str(project_path), compare_fields=True)

    assert result['status'] == 'success'
    assert os.path.exists(result['report_path'])

    with open(result['report_path'], 'r') as f:
        report_data = json.load(f)

    detailed_results = report_data['detailed_results']
    assert "field_comparison_analysis" in detailed_results

    # Busca pelo resultado da comparação do data2.csv
    comparison_result = next((item for item in detailed_results['field_comparison_analysis'] if item['file'] == 'data2.csv'), None)

    assert comparison_result is not None
    assert comparison_result['status'] == 'Inconsistente'
    assert 'missing_columns' in comparison_result
    assert 'extra_columns' in comparison_result
    assert 'name' in comparison_result['missing_columns']
    assert 'age' in comparison_result['extra_columns']


def test_return_structure_on_no_files_found(tmp_path):
    """
    Garante que a função retorna a estrutura de dicionário esperada
    mesmo quando nenhum arquivo de dados é encontrado no diretório.
    """
    empty_dir = tmp_path / "empty_project"
    empty_dir.mkdir()

    result = run_discovery_logic(data_project_path=str(empty_dir))

    assert result['status'] == 'success'
    assert result['message'] == 'Nenhum arquivo encontrado para análise.'
    assert result['report_path'] is None

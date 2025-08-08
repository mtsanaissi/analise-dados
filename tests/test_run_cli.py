# -*- coding: utf-8 -*-

import subprocess
import os
import sys
import pytest

# Define o diretório base para os dados de teste
TEST_DATA_DIR = os.path.join("tests", "data", "cli_test_data")
# Define o diretório de saída para os relatórios de teste
TEST_OUTPUT_DIR = os.path.join(TEST_DATA_DIR, "output")


@pytest.fixture(scope="module")
def setup_test_environment():
    """
    Configura o ambiente de teste, criando diretórios e arquivos necessários.
    Este fixture é executado uma vez por módulo.
    """
    # Cria os diretórios de dados e de saída
    os.makedirs(TEST_OUTPUT_DIR, exist_ok=True)

    # Cria um arquivo CSV de teste
    csv_content = "id;name;value\n1;test1;100\n2;test2;200"
    with open(os.path.join(TEST_DATA_DIR, "sample.csv"), "w") as f:
        f.write(csv_content)

    # Cria um arquivo de consulta para o teste de enrich
    lookup_content = "id;extra_info\n1;info1\n2;info2"
    with open(os.path.join(TEST_DATA_DIR, "lookup.csv"), "w") as f:
        f.write(lookup_content)

    # Cria um arquivo de configuração para o teste de correct_values
    config_content = """
file_rules:
  - file_pattern: "*.csv"
    corrections:
      - column: "name"
        existing_value: "test1"
        new_value: "TEST_ONE"
"""
    with open(os.path.join(TEST_DATA_DIR, "correct_config.yml"), "w") as f:
        f.write(config_content)

    yield

    # Limpeza (opcional, pode ser útil se os testes falharem)
    # import shutil
    # shutil.rmtree(TEST_DATA_DIR)


def run_cli_command(command: list) -> subprocess.CompletedProcess:
    """
    Executa um comando da CLI usando subprocess.

    Args:
        command (list): A lista de argumentos do comando.

    Returns:
        subprocess.CompletedProcess: O resultado da execução do comando.
    """
    base_command = [sys.executable, os.path.join("src", "run.py")]
    full_command = base_command + command
    return subprocess.run(full_command, capture_output=True, text=True, check=False)


def test_discovery_command_success(setup_test_environment):
    """
    Testa se o comando 'discovery' é executado com sucesso e gera a saída esperada.
    """
    command = ["discovery", "--data-project-path", TEST_DATA_DIR, "--report-output", "json"]
    result = run_cli_command(command)

    assert result.returncode == 0
    assert "Fase de Descoberta e Diagnóstico concluída com sucesso." in result.stdout
    assert "Relatório gerado em:" in result.stdout

    # Verifica se o relatório foi criado
    report_path = os.path.join(TEST_DATA_DIR, "fad-metadados", "discovery_report.json")
    assert os.path.exists(report_path)


def test_treatment_enrich_command_success(setup_test_environment):
    """
    Testa se o sub-comando 'treatment enrich' é executado com sucesso.
    """
    output_file = os.path.join(TEST_OUTPUT_DIR, "enriched_output.csv")
    command = [
        "treatment", "enrich",
        "--main-file", os.path.join(TEST_DATA_DIR, "sample.csv"),
        "--lookup-file", os.path.join(TEST_DATA_DIR, "lookup.csv"),
        "--main-key", "id",
        "--lookup-key", "id",
        "--columns-to-add", "extra_info",
        "--output-file", output_file,
        "--sep", ";"
    ]
    result = run_cli_command(command)

    assert result.returncode == 0
    assert "Enriquecimento de dados concluído." in result.stdout
    assert os.path.exists(output_file)


def test_treatment_correct_values_command_success(setup_test_environment):
    """
    Testa se o sub-comando 'treatment correct_values' é executado com sucesso.
    """
    # Primeiro, crie uma cópia do arquivo original para não modificar o teste de discovery
    source_file = os.path.join(TEST_DATA_DIR, "sample.csv")
    target_dir = os.path.join(TEST_DATA_DIR, "correct_values_test")
    os.makedirs(target_dir, exist_ok=True)
    target_file = os.path.join(target_dir, "sample_to_correct.csv")
    import shutil
    shutil.copy(source_file, target_file)

    command = [
        "treatment", "correct_values",
        "--data-project-path", target_dir,
        "--config-file", os.path.join(TEST_DATA_DIR, "correct_config.yml")
    ]
    result = run_cli_command(command)

    assert result.returncode == 0
    assert "Operação 'correct_values' concluída." in result.stdout

    # Verifica se o arquivo foi modificado
    with open(target_file, "r") as f:
        content = f.read()
        assert "TEST_ONE" in content
        assert "test1" not in content

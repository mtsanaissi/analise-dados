# -*- coding: utf-8 -*-

import csv
import subprocess
import os
import sys
import shutil
import pytest

# Define o diretório base para os dados de teste
TEST_DATA_DIR = os.path.join("tests", "data", "cli_test_data")
# Define o diretório de saída para os relatórios de teste
TEST_OUTPUT_DIR = os.path.join(TEST_DATA_DIR, "output")
OPS_LOG_PATH = os.path.join(TEST_DATA_DIR, "fad-metadados", "ops.csv")


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

    if os.path.exists(OPS_LOG_PATH):
        os.remove(OPS_LOG_PATH)

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
    base_command = [sys.executable, "-m", "src.run"]
    full_command = base_command + command
    return subprocess.run(full_command, capture_output=True, text=True, check=False)


def read_ops_rows() -> list[list[str]]:
    """
    Lê o arquivo `ops.csv` de teste e retorna suas linhas.

    Returns:
        list[list[str]]: Linhas do CSV, incluindo o cabeçalho.
    """
    with open(OPS_LOG_PATH, "r", encoding="utf-8", newline="") as file_handler:
        return list(csv.reader(file_handler))


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
    assert os.path.exists(OPS_LOG_PATH)

    ops_rows = read_ops_rows()
    assert ops_rows[1][1] == "discovery"
    assert "--data-project-path tests/data/cli_test_data" in ops_rows[1][2]
    assert "--report-output json" in ops_rows[1][2]


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

    ops_rows = read_ops_rows()
    assert any(row[1] == "treatment.enrich" for row in ops_rows[1:])


def test_treatment_correct_values_command_success(setup_test_environment):
    """
    Testa se o sub-comando 'treatment correct_values' é executado com sucesso.
    """
    # Primeiro, crie uma cópia do arquivo original para não modificar o teste de discovery
    source_file = os.path.join(TEST_DATA_DIR, "sample.csv")
    target_dir = os.path.join(TEST_DATA_DIR, "correct_values_test")
    os.makedirs(target_dir, exist_ok=True)
    target_file = os.path.join(target_dir, "sample_to_correct.csv")
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

    ops_rows = read_ops_rows()
    assert any(row[1] == "treatment.correct_values" for row in ops_rows[1:])


def test_treatment_rename_columns_command_success(setup_test_environment):
    """
    Testa se o sub-comando 'treatment rename_columns' renomeia colunas de um CSV.
    """
    source_file = os.path.join(TEST_DATA_DIR, "sample.csv")
    renamed_file = os.path.join(TEST_OUTPUT_DIR, "renamed_sample.csv")
    shutil.copy(source_file, renamed_file)

    command = [
        "treatment", "rename_columns",
        "--input-file", renamed_file,
        "--old-columns", "id", "name",
        "--new-columns", "codigo", "nome",
        "--delimiter", ";"
    ]
    result = run_cli_command(command)

    assert result.returncode == 0
    assert "Renomeação de colunas concluída com sucesso." in result.stdout

    with open(renamed_file, "r", encoding="utf-8") as file_handler:
        content = file_handler.read()
        assert content.startswith("codigo;nome;value")

    ops_rows = read_ops_rows()
    rename_rows = [row for row in ops_rows[1:] if row[1] == "treatment.rename_columns"]
    assert rename_rows
    assert "--input-file" in rename_rows[-1][2]
    assert "--old-columns id name" in rename_rows[-1][2]
    assert "--new-columns codigo nome" in rename_rows[-1][2]


def test_treatment_rename_columns_error_does_not_append_log(setup_test_environment):
    """
    Testa que falhas na CLI não geram novas entradas no `ops.csv`.
    """
    existing_row_count = len(read_ops_rows())
    missing_file = os.path.join(TEST_OUTPUT_DIR, "arquivo_inexistente.csv")
    command = [
        "treatment", "rename_columns",
        "--input-file", missing_file,
        "--old-columns", "id",
        "--new-columns", "codigo",
    ]

    result = run_cli_command(command)

    assert result.returncode == 1
    assert "Arquivo de entrada não encontrado" in result.stdout
    assert len(read_ops_rows()) == existing_row_count

# -*- coding: utf-8 -*-
import os
import pandas as pd
import pytest
from src import utils

def test_find_files(tmp_path):
    """Testa a função find_files para encontrar arquivos com extensões específicas."""
    # Arrange
    d = tmp_path / "sub"
    d.mkdir()
    f1 = d / "test1.csv"
    f2 = d / "test2.txt"
    f3 = tmp_path / "test3.csv"
    f1.write_text("content")
    f2.write_text("content")
    f3.write_text("content")

    # Act
    csv_files = utils.find_files(str(tmp_path), ["csv"])

    # Assert
    assert len(csv_files) == 2
    assert str(f1) in csv_files
    assert str(f3) in csv_files

def test_find_files_recursively(tmp_path):
    """Testa a busca recursiva de arquivos."""
    # Arrange
    d = tmp_path / "sub"
    d.mkdir()
    f1 = d / "test1.csv"
    f1.write_text("content")

    # Act
    csv_files = utils.find_files(str(tmp_path), ["csv"], recursive=True)

    # Assert
    assert len(csv_files) == 1
    assert str(f1) in csv_files

def test_find_files_not_recursively(tmp_path):
    """Testa a busca não recursiva de arquivos."""
    # Arrange
    d = tmp_path / "sub"
    d.mkdir()
    (d / "test1.csv").write_text("content")
    f2 = tmp_path / "test2.csv"
    f2.write_text("content")

    # Act
    csv_files = utils.find_files(str(tmp_path), ["csv"], recursive=False)

    # Assert
    assert len(csv_files) == 1
    assert str(f2) in csv_files

def test_find_files_with_exclude_patterns(tmp_path):
    """Testa a exclusão de arquivos baseada em padrões."""
    # Arrange
    (tmp_path / "a_report.csv").write_text("content")
    (tmp_path / "temp_b.csv").write_text("content")
    f3 = tmp_path / "data.csv"
    f3.write_text("content")

    # Act
    csv_files = utils.find_files(str(tmp_path), ["csv"], exclude_patterns=['*_report.csv', 'temp_*'])

    # Assert
    assert len(csv_files) == 1
    assert str(f3) in csv_files

def test_find_files_with_default_excluded_dirs(tmp_path):
    """Testa a exclusão de diretórios padrão como 'fad-metadados' e 'fad-bkp*'."""
    # Arrange
    # Diretórios e arquivos que devem ser ignorados
    (tmp_path / "fad-metadados").mkdir()
    (tmp_path / "fad-metadados" / "meta.csv").write_text("metadata")

    (tmp_path / "fad-config").mkdir()
    (tmp_path / "fad-config" / "config.csv").write_text("config")

    (tmp_path / "fad-bkp-2025-01-01").mkdir()
    (tmp_path / "fad-bkp-2025-01-01" / "backup.csv").write_text("backup")

    # Arquivo que deve ser encontrado
    f_valid = tmp_path / "data.csv"
    f_valid.write_text("content")

    # Act
    found_files = utils.find_files(str(tmp_path), ["csv"])

    # Assert
    assert len(found_files) == 1
    assert str(f_valid) in found_files

def test_read_csv_robust(tmp_path):
    """Testa a leitura de um arquivo CSV válido."""
    # Arrange
    p = tmp_path / "test.csv"
    p.write_text("col1;col2\n1;2", encoding="utf-8")

    # Act
    df = utils.read_csv_robust(str(p))

    # Assert
    assert isinstance(df, pd.DataFrame)
    assert not df.empty
    assert df.columns.tolist() == ["col1", "col2"]
    assert df.iloc[0, 0] == 1

def test_read_csv_robust_file_not_found(capfd):
    """Testa a leitura de um arquivo CSV inexistente."""
    # Act
    df = utils.read_csv_robust("non_existent_file.csv")

    # Assert
    assert df is None
    out, err = capfd.readouterr()
    assert "Erro: Arquivo não encontrado" in err

def test_has_problematic_char():
    """Testa a detecção de caracteres problemáticos."""
    assert utils.has_problematic_char("abc\ufffd") is True
    assert utils.has_problematic_char("abc\x01") is True
    assert utils.has_problematic_char("normal text") is False
    assert utils.has_problematic_char("text with\ttab") is False
    assert utils.has_problematic_char(123) is False

def test_save_df_to_csv(tmp_path):
    """Testa se o DataFrame é salvo corretamente em um arquivo CSV."""
    # Arrange
    df = pd.DataFrame({"a": [1], "b": [2]})
    p = tmp_path / "output.csv"

    # Act
    result = utils.save_df_to_csv(df, str(p))

    # Assert
    assert result is True
    assert p.exists()
    read_df = pd.read_csv(str(p), sep=';')
    pd.testing.assert_frame_equal(df, read_df)

@pytest.mark.parametrize("discovery_args, expected_fragment", [
    ({"compare_fields": True}, ["--compare-fields"]),
    ({"compare_types": True}, ["--compare-types"]),
    ({"report_output": "json"}, ["--report-output", "json"]),
    ({"report_output": "html"}, ["--report-output", "html"]),
    ({"char_cleanup_path": "/path/to/config"}, ["--generate-char-cleanup-config", "/path/to/config"]),
    (
        {
            "compare_fields": True,
            "compare_types": True,
            "report_output": "html",
            "char_cleanup_path": "/path/to/config"
        },
        [
            "--compare-fields",
            "--compare-types",
            "--report-output", "html",
            "--generate-char-cleanup-config", "/path/to/config"
        ]
    ),
])
def test_build_command_discovery_phase(discovery_args, expected_fragment):
    """
    Testa a construção de comandos para a fase 'discovery' com diferentes argumentos.
    """
    # Arrange
    project_path = "/fake/project"

    # Act
    command = utils.build_command(project_path, "discovery", discovery_args=discovery_args)

    # Assert
    assert all(item in command for item in expected_fragment)
    assert command[3] == project_path
    assert command[5] == "discovery"

@pytest.mark.parametrize("treatment_args, expected_fragment", [
    ({"operation": "Remover Espaços"}, ["--strip-whitespace"]),
    (
        {"operation": "Substituir Valores", "config_file_path": "/path/to/config.json"},
        ["--replace-values", "/path/to/config.json"]
    ),
    (
        {"operation": "Encontrar e Substituir Texto", "config_file_path": "/path/to/find.json"},
        ["--find-and-replace-text", "/path/to/find.json"]
    ),
    (
        {
            "operation": "Concatenar Dados",
            "input_folder": "input",
            "output_file": "output.csv",
            "file_type": "csv",
        },
        ["--concatenate-data", "--input-folder", "input", "--output-file", "output.csv", "--file-type", "csv"],
    ),
    (
        {
            "operation": "Enriquecer Dados",
            "main_file": "main.csv",
            "lookup_file": "lookup.csv",
            "main_key": "id",
            "lookup_key": "id",
            "columns_to_add": ["col1", "col2"],
            "output_file": "enriched.csv",
        },
        [
            "--enrich-data",
            "--main-file", "main.csv",
            "--lookup-file", "lookup.csv",
            "--main-key", "id",
            "--lookup-key", "id",
            "--columns-to-add", "col1,col2",
            "--output-file", "enriched.csv",
        ],
    ),
    # Testa um caso onde o caminho do arquivo de configuração não é fornecido
    ({"operation": "Substituir Valores"}, ["--replace-values"]),
])
def test_build_command_treatment_phase(treatment_args, expected_fragment):
    """
    Testa a construção de comandos para a fase 'treatment' com diferentes operações.
    """
    # Arrange
    project_path = "/fake/project"

    # Act
    command = utils.build_command(project_path, "treatment", treatment_args=treatment_args)

    # Assert
    assert all(item in command for item in expected_fragment)
    assert command[3] == project_path
    assert command[5] == "treatment"

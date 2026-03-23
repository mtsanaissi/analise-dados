# -*- coding: utf-8 -*-
import csv
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


def test_build_operation_parameters_discovery():
    """Testa a serialização textual dos parâmetros de discovery."""
    project_path = "/tmp/data/projeto_a"

    parameters = utils.build_operation_parameters(
        "discovery",
        {
            "data_project_path": project_path,
            "extensions": ['csv', 'xlsx', 'xls', 'json', 'txt'],
            "recursive": True,
            "output_format": "text",
            "report_output": "json",
            "compare_fields": True,
            "compare_types": False,
            "generate_char_cleanup_config": None,
        },
    )

    assert parameters == f"--data-project-path {project_path} --report-output json --compare-fields"


def test_resolve_data_project_path_with_explicit_project(tmp_path):
    """Testa a resolução de projeto quando o caminho explícito é fornecido."""
    project_dir = tmp_path / "workspace" / "data" / "projeto_a"
    project_dir.mkdir(parents=True)

    resolved_path = utils.resolve_data_project_path(explicit_project_path=str(project_dir))

    assert resolved_path == str(project_dir.resolve())


def test_resolve_data_project_path_with_explicit_nested_path(tmp_path):
    """Testa a normalização de um caminho explícito para a raiz do projeto."""
    nested_dir = tmp_path / "workspace" / "data" / "projeto_a" / "subpasta"
    nested_dir.mkdir(parents=True)

    resolved_path = utils.resolve_data_project_path(explicit_project_path=str(nested_dir))

    assert resolved_path == str((tmp_path / "workspace" / "data" / "projeto_a").resolve())


def test_resolve_data_project_path_from_relative_and_absolute_candidates(tmp_path, monkeypatch):
    """Testa a resolução de projeto a partir de caminhos relativos e absolutos."""
    workspace_dir = tmp_path / "workspace"
    project_dir = workspace_dir / "data" / "projeto_a"
    file_path = project_dir / "arquivo.csv"
    file_path.parent.mkdir(parents=True)
    file_path.write_text("conteudo", encoding="utf-8")
    monkeypatch.chdir(workspace_dir)

    resolved_path = utils.resolve_data_project_path(
        candidate_paths=["data/projeto_a/arquivo.csv", str(file_path.resolve())],
    )

    assert resolved_path == str(project_dir.resolve())


def test_resolve_data_project_path_ignores_paths_outside_data(tmp_path):
    """Testa que caminhos fora de `data/*` não influenciam a resolução."""
    external_file = tmp_path / "tmp" / "config.yml"
    external_file.parent.mkdir(parents=True)
    external_file.write_text("valor: 1", encoding="utf-8")

    resolved_path = utils.resolve_data_project_path(candidate_paths=[str(external_file)])

    assert resolved_path is None


def test_resolve_data_project_path_returns_none_for_ambiguous_paths(tmp_path):
    """Testa a detecção de caminhos ambíguos entre dois projetos."""
    project_a = tmp_path / "data" / "projeto_a" / "arquivo.csv"
    project_b = tmp_path / "data" / "projeto_b" / "arquivo.csv"
    project_a.parent.mkdir(parents=True)
    project_b.parent.mkdir(parents=True)
    project_a.write_text("a", encoding="utf-8")
    project_b.write_text("b", encoding="utf-8")

    resolved_path = utils.resolve_data_project_path(
        candidate_paths=[str(project_a), str(project_b)],
    )

    assert resolved_path is None


def test_log_project_operation_creates_header_and_row(tmp_path):
    """Testa a criação do `ops.csv` com cabeçalho e primeira linha."""
    project_dir = tmp_path / "data" / "projeto_ops"
    project_dir.mkdir(parents=True)

    ops_log_path = utils.log_project_operation(
        operation_name="discovery",
        operation_args={
            "data_project_path": str(project_dir),
            "report_output": "json",
            "compare_fields": True,
        },
        explicit_project_path=str(project_dir),
    )

    assert ops_log_path == str((project_dir / utils.METADATA_DIR / utils.OPS_LOG_FILENAME).resolve())

    with open(ops_log_path, "r", encoding="utf-8", newline="") as file_handler:
        rows = list(csv.reader(file_handler))

    assert rows[0] == ["timestamp", "operation", "parameters"]
    assert rows[1][1] == "discovery"
    assert rows[1][2] == f"--data-project-path {project_dir.resolve()} --report-output json --compare-fields"


def test_log_project_operation_appends_multiple_rows(tmp_path):
    """Testa o append de múltiplas operações no mesmo arquivo."""
    project_dir = tmp_path / "data" / "projeto_ops"
    project_dir.mkdir(parents=True)

    utils.log_project_operation(
        operation_name="treatment.remove_whitespace",
        operation_args={"data_project_path": str(project_dir)},
        explicit_project_path=str(project_dir),
    )
    utils.log_project_operation(
        operation_name="treatment.transform_columns",
        operation_args={"data_project_path": str(project_dir)},
        explicit_project_path=str(project_dir),
    )

    ops_log_path = project_dir / utils.METADATA_DIR / utils.OPS_LOG_FILENAME
    with open(ops_log_path, "r", encoding="utf-8", newline="") as file_handler:
        rows = list(csv.reader(file_handler))

    assert len(rows) == 3
    assert rows[1][1] == "treatment.remove_whitespace"
    assert rows[2][1] == "treatment.transform_columns"


def test_log_project_operation_escapes_parameters_with_commas_and_quotes(tmp_path):
    """Testa o escape correto do campo de parâmetros no CSV."""
    project_dir = tmp_path / "data" / "projeto_ops"
    input_file = project_dir / 'arquivo "a,b".csv'
    project_dir.mkdir(parents=True)
    input_file.write_text("id;nome\n1;teste", encoding="utf-8")

    ops_log_path = utils.log_project_operation(
        operation_name="treatment.rename_columns",
        operation_args={
            "input_file": str(input_file),
            "old_columns": ["id", 'nome, "antigo"'],
            "new_columns": ["codigo", "nome_novo"],
            "delimiter": ";",
        },
        explicit_project_path=str(project_dir),
    )

    with open(ops_log_path, "r", encoding="utf-8") as file_handler:
        raw_content = file_handler.read()

    assert '""' in raw_content

    with open(ops_log_path, "r", encoding="utf-8", newline="") as file_handler:
        rows = list(csv.reader(file_handler))

    assert rows[1][1] == "treatment.rename_columns"
    assert '--old-columns id' in rows[1][2]
    assert 'nome, \\"antigo\\"' in rows[1][2]


def test_log_project_operation_skips_when_project_resolution_is_ambiguous(tmp_path):
    """Testa o não registro quando os caminhos apontam para projetos diferentes."""
    project_a = tmp_path / "data" / "projeto_a" / "arquivo.csv"
    project_b = tmp_path / "data" / "projeto_b" / "saida.csv"
    project_a.parent.mkdir(parents=True)
    project_b.parent.mkdir(parents=True)
    project_a.write_text("a", encoding="utf-8")
    project_b.write_text("b", encoding="utf-8")

    ops_log_path = utils.log_project_operation(
        operation_name="treatment.rename_columns",
        operation_args={
            "input_file": str(project_a),
            "old_columns": ["id"],
            "new_columns": ["codigo"],
            "output_file": str(project_b),
        },
        candidate_paths=[str(project_a), str(project_b)],
    )

    assert ops_log_path is None
    assert not (tmp_path / "data" / "projeto_a" / utils.METADATA_DIR / utils.OPS_LOG_FILENAME).exists()
    assert not (tmp_path / "data" / "projeto_b" / utils.METADATA_DIR / utils.OPS_LOG_FILENAME).exists()

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
    assert command[:4] == [utils.sys.executable, "-m", "src.run", "discovery"]
    assert command[4:6] == ["--data-project-path", project_path]

@pytest.mark.parametrize("treatment_args, expected_fragment", [
    ({"operation": "Remover Espaços"}, ["remove_whitespace", "--data-project-path", "/fake/project"]),
    (
        {"operation": "Substituir Valores", "config_file_path": "/path/to/config.json"},
        ["correct_values", "--data-project-path", "/fake/project", "--config-file", "/path/to/config.json"]
    ),
    (
        {"operation": "Encontrar e Substituir Texto", "config_file_path": "/path/to/find.json"},
        ["replace_text", "--data-project-path", "/fake/project", "--config-file", "/path/to/find.json"]
    ),
    (
        {
            "operation": "Concatenar Dados",
            "input_folder": "input",
            "output_file": "output.csv",
            "file_type": "csv",
        },
        ["concatenate", "--data-project-path", "input", "--output-file", "output.csv", "--file-type", "csv"],
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
            "enrich",
            "--main-file", "main.csv",
            "--lookup-file", "lookup.csv",
            "--main-key", "id",
            "--lookup-key", "id",
            "--columns-to-add", "col1", "col2",
            "--output-file", "enriched.csv",
        ],
    ),
    # Testa um caso onde o caminho do arquivo de configuração não é fornecido
    ({"operation": "Substituir Valores"}, ["correct_values", "--data-project-path", "/fake/project"]),
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
    assert command[:4] == [utils.sys.executable, "-m", "src.run", "treatment"]

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

def test_find_files_with_custom_excluded_dirs(tmp_path):
    """Testa se a passagem de uma lista de exclusão personalizada sobrepõe a padrão."""
    # Arrange
    # Diretório que seria ignorado por padrão, mas não deve ser com a lista personalizada
    (tmp_path / "fad-metadados").mkdir()
    f_meta = tmp_path / "fad-metadados" / "meta.csv"
    f_meta.write_text("metadata")

    # Diretório que deve ser ignorado pela lista personalizada
    (tmp_path / "custom-ignore").mkdir()
    (tmp_path / "custom-ignore" / "ignored.csv").write_text("ignored")

    f_valid = tmp_path / "data.csv"
    f_valid.write_text("content")

    # Act
    # Passa uma lista de exclusão vazia, esperando que NADA seja ignorado
    found_files_custom_empty = utils.find_files(str(tmp_path), ["csv"], exclude_dirs=[])

    # Passa uma lista de exclusão personalizada
    found_files_custom = utils.find_files(str(tmp_path), ["csv"], exclude_dirs=['custom-ignore'])

    # Assert
    assert len(found_files_custom_empty) == 3
    assert str(f_meta) in found_files_custom_empty
    assert str(f_valid) in found_files_custom_empty

    assert len(found_files_custom) == 2
    assert str(f_meta) in found_files_custom
    assert str(f_valid) in found_files_custom

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

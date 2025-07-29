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

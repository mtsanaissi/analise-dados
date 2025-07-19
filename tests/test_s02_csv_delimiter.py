# -*- coding: utf-8 -*-
"""
Testes para o script src/s02_csv_delimiter.py.
"""

import os
import sys
import pytest
import csv
from unittest.mock import patch, call

# Adiciona o diretório src ao sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.discovery.s02_csv_delimiter import (
    detect_csv_delimiter,
    main as delimiter_main
)

# --- Fixtures ---

@pytest.fixture
def temp_csv_dir(tmp_path):
    """Cria um diretório temporário com arquivos CSV para teste."""
    csv_dir = tmp_path / "csv_data"
    csv_dir.mkdir()

    # CSV com ponto e vírgula
    (csv_dir / "semicolon.csv").write_text("h1;h2\nv1;v2", encoding="utf-8")

    # CSV com vírgula
    (csv_dir / "comma.csv").write_text("h1,h2\nv1,v2", encoding="latin-1")

    # CSV com TAB
    (csv_dir / "tab.tsv").write_text("h1\th2\nv1\tv2", encoding="utf-8")

    # Arquivo vazio
    (csv_dir / "empty.csv").touch()

    # Arquivo não-CSV para ser ignorado
    (csv_dir / "other.txt").write_text("some text", encoding="utf-8")
    
    # Arquivo com formato inconsistente que faz o Sniffer falhar
    (csv_dir / "inconsistent.csv").write_text("thisisjustonelonglineoftextwithoutdelimiters", encoding="utf-8")

    return csv_dir

# --- Testes Unitários ---

def test_detect_delimiter_semicolon(temp_csv_dir):
    """Testa a detecção de ponto e vírgula como delimitador."""
    result = detect_csv_delimiter(str(temp_csv_dir / "semicolon.csv"))
    assert result["delimitador"] == ";"
    assert result["erro"] is None

def test_detect_delimiter_comma(temp_csv_dir):
    """Testa a detecção de vírgula como delimitador."""
    result = detect_csv_delimiter(str(temp_csv_dir / "comma.csv"))
    assert result["delimitador"] == ","
    assert result["encoding"] is not None

def test_detect_delimiter_tab(temp_csv_dir):
    """Testa a detecção de TAB como delimitador."""
    result = detect_csv_delimiter(str(temp_csv_dir / "tab.tsv"))
    assert result["delimitador"] == "\t"

def test_detect_delimiter_empty_file(temp_csv_dir):
    """Testa o comportamento com um arquivo CSV vazio."""
    result = detect_csv_delimiter(str(temp_csv_dir / "empty.csv"))
    assert result["delimitador"] is None
    assert result["erro"] == "Arquivo vazio"

def test_detect_delimiter_sniffer_error(temp_csv_dir):
    """Testa o tratamento de erro quando o csv.Sniffer falha."""
    file_path = str(temp_csv_dir / "semicolon.csv")  # Pode ser qualquer arquivo válido
    
    # Força o Sniffer a levantar um erro para testar o bloco except
    with patch('src.discovery.s02_csv_delimiter.csv.Sniffer.sniff', side_effect=csv.Error("mocked error")):
        result = detect_csv_delimiter(file_path)
    
    assert result["delimitador"] is None
    assert "Sniffer não conseguiu determinar" in result["erro"]

# --- Teste de Integração ---

@patch('sys.stdout')
def test_main_integration_console_output(mock_stdout, temp_csv_dir):
    """Testa a execução completa e a saída no console."""
    test_args = [
        "s02_csv_delimiter.py",
        "-d", str(temp_csv_dir),
        "--recursive"
    ]

    with patch.object(sys, 'argv', test_args):
        delimiter_main()

    output = "".join(call.args[0] for call in mock_stdout.write.call_args_list)

    # Verifica se os arquivos foram processados e os delimitadores corretos mostrados
    assert "semicolon.csv" in output
    assert "';'" in output
    assert "comma.csv" in output
    assert "','" in output
    # O nome do arquivo .tsv não deve aparecer pois o script busca por .csv
    assert "tab.tsv" not in output
    assert "empty.csv" in output
    assert "Arquivo vazio" in output

@patch('src.discovery.s02_csv_delimiter.pd.DataFrame.to_csv')
def test_main_integration_report_saving(mock_to_csv, temp_csv_dir):
    """Testa a funcionalidade de salvar o relatório em CSV."""
    report_path = temp_csv_dir / "report.csv"
    test_args = [
        "s02_csv_delimiter.py",
        "-d", str(temp_csv_dir),
        "-o", str(report_path)
    ]

    with patch.object(sys, 'argv', test_args):
        delimiter_main()

    # Verifica se a função to_csv foi chamada com o caminho correto
    mock_to_csv.assert_called_once()
    call_args, call_kwargs = mock_to_csv.call_args
    assert call_args[0] == str(report_path)
    assert call_kwargs['index'] is False
    assert 'utf-8-sig' in call_kwargs['encoding']

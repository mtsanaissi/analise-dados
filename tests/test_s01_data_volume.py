# -*- coding: utf-8 -*-
"""
Testes para o script src/s01_data_volume.py.
"""

import os
import sys
import pytest
import pandas as pd
from unittest.mock import patch, call

# Adiciona o diretório src ao sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.discovery.s01_data_volume import (
    format_bytes,
    get_file_metrics,
    main as data_volume_main
)

# --- Fixtures ---

@pytest.fixture
def temp_data_dir(tmp_path):
    """Cria um diretório de dados temporário com arquivos de teste."""
    data_dir = tmp_path / "data"
    data_dir.mkdir()

    # CSV
    (data_dir / "test_data.csv").write_text("col1;col2\n1;a\n2;b\n3;c", encoding="utf-8")

    # Excel
    excel_path = data_dir / "test_data.xlsx"
    with pd.ExcelWriter(excel_path) as writer:
        pd.DataFrame({'col1': range(5)}).to_excel(writer, sheet_name='Sheet1', index=False)
        pd.DataFrame({'col2': ['a', 'b']}).to_excel(writer, sheet_name='Sheet2', index=False)

    # JSON (lista de objetos)
    (data_dir / "list.json").write_text('[{"id": 1}, {"id": 2}]', encoding="utf-8")
    
    # JSON (objeto único)
    (data_dir / "single.json").write_text('{"name": "test"}', encoding="utf-8")

    # Arquivo vazio
    (data_dir / "empty.csv").touch()

    # Arquivo de outro tipo
    (data_dir / "document.txt").write_text("ignore this", encoding="utf-8")

    return data_dir

# --- Testes Unitários ---

@pytest.mark.parametrize("size, expected", [
    (500, "500 B"),
    (2048, "2.00 KB"),
    (1572864, "1.50 MB"),
    (2147483648, "2.00 GB"),
    (0, "0 B")
])
def test_format_bytes(size, expected):
    """Testa a formatação de bytes para unidades legíveis."""
    assert format_bytes(size) == expected

def test_get_file_metrics_csv(temp_data_dir):
    """Testa a extração de métricas de um arquivo CSV."""
    file_path = temp_data_dir / "test_data.csv"
    metrics = get_file_metrics(str(file_path), delimiter=';')
    assert metrics["registros"] == 3
    assert metrics["tamanho_bytes"] > 0
    assert metrics["erro"] is None

def test_get_file_metrics_excel(temp_data_dir):
    """Testa a extração de métricas de um arquivo Excel com múltiplas abas."""
    file_path = temp_data_dir / "test_data.xlsx"
    metrics = get_file_metrics(str(file_path), delimiter=';')
    # 5 registros na Sheet1 + 2 na Sheet2
    assert metrics["registros"] == 7
    assert metrics["tamanho_bytes"] > 0
    assert metrics["erro"] is None

def test_get_file_metrics_json_list(temp_data_dir):
    """Testa a extração de métricas de um arquivo JSON (lista)."""
    file_path = temp_data_dir / "list.json"
    metrics = get_file_metrics(str(file_path), delimiter=';')
    assert metrics["registros"] == 2
    assert metrics["tamanho_bytes"] > 0
    assert metrics["erro"] is None

def test_get_file_metrics_empty_file(temp_data_dir):
    """Testa a extração de métricas de um arquivo vazio."""
    file_path = temp_data_dir / "empty.csv"
    metrics = get_file_metrics(str(file_path), delimiter=';')
    assert metrics["registros"] == 0
    assert metrics["tamanho_bytes"] == 0
    assert metrics["erro"] is None

# --- Teste de Integração ---

@patch('sys.stdout')
def test_main_integration_summary_output(mock_stdout, temp_data_dir):
    """
    Testa a execução completa do script e verifica a saída do resumo no console.
    """
    test_args = [
        "s01_data_volume.py",
        "-d", str(temp_data_dir),
        "-e", "csv", "xlsx", "json",
        "--recursive"
    ]

    with patch.object(sys, 'argv', test_args):
        data_volume_main()

    # Captura a saída e verifica se as informações essenciais estão presentes
    output = "".join(call.args[0] for call in mock_stdout.write.call_args_list)
    
    assert "Resumo de Volume e Tamanho por Extensão" in output
    assert "csv" in output
    assert "xlsx" in output
    assert "json" in output
    # Verifica se o total de registros CSV (3 + 0) está correto
    assert "3" in output 
    # Verifica se o total de registros XLSX (7) está correto
    assert "7" in output
    # Verifica se o total de registros JSON (2 + 1) está correto
    assert "3" in output
    assert "TOTAL GERAL" in output
    assert "13" in output # 3 (csv) + 7 (xlsx) + 3 (json)

@patch('src.discovery.s01_data_volume.pd.DataFrame.to_csv')
def test_main_integration_save_report(mock_to_csv, temp_data_dir):
    """
    Testa a execução completa com a flag para salvar o relatório em CSV.
    """
    output_path = temp_data_dir / "report.csv"
    test_args = [
        "s01_data_volume.py",
        "-d", str(temp_data_dir),
        "-o", str(output_path)
    ]

    with patch.object(sys, 'argv', test_args):
        data_volume_main()

    # Verifica se a função to_csv foi chamada com o caminho correto
    mock_to_csv.assert_called_once_with(
        str(output_path), index=False, encoding='utf-8-sig'
    )

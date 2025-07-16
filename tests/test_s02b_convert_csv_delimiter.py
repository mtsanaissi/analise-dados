# -*- coding: utf-8 -*-
"""
Testes para o script src/s02b_convert_csv_delimiter.py.
"""

import os
import sys
import pytest
import pandas as pd
from unittest.mock import patch, call

# Adiciona o diretório src ao sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

# A importação deve ser feita após a modificação do path
from s02b_convert_csv_delimiter import main as convert_delimiter_main

# --- Fixtures ---

@pytest.fixture
def temp_dirs(tmp_path):
    """Cria diretórios de origem e destino para os testes."""
    source_dir = tmp_path / "source"
    output_dir = tmp_path / "output"
    source_dir.mkdir()
    output_dir.mkdir()
    
    # Arquivo na raiz
    (source_dir / "root_data.csv").write_text("col1;col2\na;1\nb;2", encoding="utf-8")
    
    # Subdiretório para teste de recursividade
    sub_dir = source_dir / "subdir"
    sub_dir.mkdir()
    (sub_dir / "nested_data.csv").write_text("hdr1;hdr2\nc;3\nd;4", encoding="utf-8")
    
    # Arquivo vazio
    (source_dir / "empty.csv").write_text("", encoding="utf-8")
    
    # Arquivo não-csv para ser ignorado
    (source_dir / "notes.txt").write_text("ignore me", encoding="utf-8")
    
    return source_dir, output_dir

# --- Teste de Integração ---

def test_integration_conversion_success_recursive(temp_dirs):
    """
    Testa o cenário de sucesso da conversão, de forma recursiva,
    verificando a estrutura de pastas e o conteúdo dos arquivos convertidos.
    """
    source_dir, output_dir = temp_dirs
    
    test_args = [
        "s02b_convert_csv_delimiter.py",
        "-d", str(source_dir),
        "-o", str(output_dir),
        "--from-delimiter", ";",
        "--to-delimiter", ",",
        "--recursive"
    ]
    
    with patch.object(sys, 'argv', test_args):
        convert_delimiter_main()
        
    # 1. Verificar se os arquivos foram criados no destino
    output_root_csv = output_dir / "root_data.csv"
    output_nested_csv = output_dir / "subdir" / "nested_data.csv"
    output_empty_csv = output_dir / "empty.csv"
    
    assert output_root_csv.exists()
    assert output_nested_csv.exists()
    assert output_empty_csv.exists()
    
    # 2. Verificar se o arquivo não-csv não foi copiado
    assert not (output_dir / "notes.txt").exists()
    
    # 3. Verificar o conteúdo e o novo delimitador
    converted_content = output_root_csv.read_text(encoding="utf-8-sig")
    assert "col1,col2" in converted_content
    assert "a,1" in converted_content
    
    nested_content = output_nested_csv.read_text(encoding="utf-8-sig")
    assert "hdr1,hdr2" in nested_content
    assert "c,3" in nested_content
    
    # 4. Verificar se o arquivo vazio resulta em um arquivo com apenas uma linha em branco
    # O pandas.to_csv escreve um newline mesmo para dataframes vazios.
    # O encoding utf-8-sig adiciona um BOM.
    assert output_empty_csv.read_text(encoding="utf-8-sig").strip() == ""

@patch('sys.stdout')
@patch('sys.exit')
def test_integration_same_source_and_output_dirs(mock_exit, mock_stdout, temp_dirs):
    """
    Testa a validação que impede o uso do mesmo diretório para origem e destino.
    """
    source_dir, _ = temp_dirs
    
    test_args = [
        "s02b_convert_csv_delimiter.py",
        "-d", str(source_dir),
        "-o", str(source_dir)
    ]
    
    with patch.object(sys, 'argv', test_args):
        convert_delimiter_main()
        
    # Verifica se sys.exit(1) foi chamado
    mock_exit.assert_called_once_with(1)
    
    # Verifica se a mensagem de erro foi impressa
    output = "".join(call.args[0] for call in mock_stdout.write.call_args_list)
    assert "O diretório de origem e de destino não podem ser os mesmos" in output

@patch('sys.stdout')
@patch('sys.exit')
def test_integration_identical_delimiters(mock_exit, mock_stdout, temp_dirs):
    """
    Testa a validação que impede a conversão quando os delimitadores são idênticos.
    """
    source_dir, output_dir = temp_dirs
    
    test_args = [
        "s02b_convert_csv_delimiter.py",
        "-d", str(source_dir),
        "-o", str(output_dir),
        "--from-delimiter", ",",
        "--to-delimiter", ","
    ]
    
    with patch.object(sys, 'argv', test_args):
        convert_delimiter_main()
        
    # Verifica se sys.exit(0) foi chamado
    mock_exit.assert_called_once_with(0)
    
    # Verifica se a mensagem de aviso foi impressa
    output = "".join(call.args[0] for call in mock_stdout.write.call_args_list)
    assert "O delimitador de origem e de destino são idênticos" in output

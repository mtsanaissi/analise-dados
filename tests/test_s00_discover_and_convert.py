# -*- coding: utf-8 -*-
"""
Testes para o script s00_discover_and_convert.py.
"""

import os
import sys
import pytest
from unittest.mock import patch

# Adiciona o diretório src ao sys.path para permitir a importação dos módulos
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.discovery.s00_discover_and_convert import (
    detect_encoding,
    convert_file_to_utf8,
    main as discover_main
)

# --- Fixtures para criação de arquivos de teste ---

@pytest.fixture
def temp_files(tmp_path):
    """
    Cria um conjunto de arquivos temporários com diferentes encodings para os testes.
    """
    # Diretório de dados simulado
    data_dir = tmp_path / "data"
    data_dir.mkdir()

    # Arquivos a serem criados
    files_to_create = {
        "utf8_file.txt": ("conteúdo com acentuação para forçar utf-8: ç ã", "utf-8"),
        "latin1_file.csv": ("conteúdo em latim-1 com acentuação", "latin-1"),
        "utf16_file.json": ('{"key": "valor com acentuação"}', "utf-16"),
        "binary_file.zip": (b"\x50\x4B\x03\x04", None)  # Assinatura de arquivo ZIP
    }

    file_paths = {}
    for name, (content, encoding) in files_to_create.items():
        file_path = data_dir / name
        if isinstance(content, str):
            file_path.write_text(content, encoding=encoding)
        else:
            file_path.write_bytes(content)
        file_paths[name] = file_path

    return data_dir, file_paths

# --- Testes para a função detect_encoding ---

def test_detect_encoding_utf8(temp_files):
    """
    Verifica se a função detecta corretamente um arquivo codificado em UTF-8.
    """
    _, file_paths = temp_files
    encoding = detect_encoding(file_paths["utf8_file.txt"])
    # A biblioteca chardet pode detectar 'ascii' para texto simples em utf-8
    assert encoding.lower() in ["utf-8", "ascii"]

def test_detect_encoding_latin1(temp_files):
    """
    Verifica se a função detecta corretamente um arquivo codificado em Latin-1.
    """
    _, file_paths = temp_files
    encoding = detect_encoding(file_paths["latin1_file.csv"])
    assert encoding.lower() in ["latin-1", "iso-8859-1"]

def test_detect_encoding_non_existent_file():
    """
    Verifica o comportamento da função ao tentar analisar um arquivo que não existe.
    """
    encoding = detect_encoding("non_existent_file.txt")
    assert encoding is None

# --- Testes para a função convert_file_to_utf8 ---

def test_convert_file_to_utf8(temp_files):
    """
    Testa a conversão de um arquivo de Latin-1 para UTF-8.
    Verifica se o backup é criado e se o conteúdo é preservado.
    """
    _, file_paths = temp_files
    latin1_path = file_paths["latin1_file.csv"]
    original_content = latin1_path.read_text(encoding="latin-1")

    # Converte o arquivo
    result = convert_file_to_utf8(latin1_path, "latin-1")
    assert result is True

    # Verifica se o backup foi criado
    backup_path = latin1_path.with_suffix(".csv.bak")
    assert backup_path.exists()

    # Verifica se o arquivo original agora é UTF-8
    try:
        converted_content = latin1_path.read_text(encoding="utf-8")
        assert converted_content == original_content
    except UnicodeDecodeError:
        pytest.fail("O arquivo convertido não pôde ser lido como UTF-8.")

    # Verifica o encoding do arquivo convertido
    final_encoding = detect_encoding(latin1_path)
    assert final_encoding.lower() in ["utf-8", "ascii"]

# --- Testes de Integração para o script principal (main) ---

@patch('sys.stdout') # Mock para capturar prints
def test_main_integration(mock_stdout, temp_files):
    """
    Testa a execução completa do script, simulando argumentos de linha de comando.
    Verifica se os arquivos corretos são convertidos e se o resumo é exibido.
    """
    data_dir, file_paths = temp_files
    
    # Simula os argumentos da linha de comando
    test_args = [
        "s00_discover_and_convert.py",
        "-d", str(data_dir),
        "-e", "csv", "json",
        "--recursive"
    ]

    with patch.object(sys, 'argv', test_args):
        discover_main()

    # Verifica se o arquivo latin-1 foi convertido
    latin1_path = file_paths["latin1_file.csv"]
    assert latin1_path.with_suffix(".csv.bak").exists()
    assert detect_encoding(latin1_path).lower() in ["utf-8", "ascii"]

    # Verifica se o arquivo utf-16 foi convertido
    utf16_path = file_paths["utf16_file.json"]
    assert utf16_path.with_suffix(".json.bak").exists()
    assert detect_encoding(utf16_path).lower() in ["utf-8", "ascii"]

    # Verifica se o arquivo utf-8 não foi modificado
    utf8_path = file_paths["utf8_file.txt"]
    assert not utf8_path.with_suffix(".txt.bak").exists()

    # Verifica se o arquivo binário não foi modificado
    binary_path = file_paths["binary_file.zip"]
    assert not binary_path.with_suffix(".zip.bak").exists()

# -*- coding: utf-8 -*-
"""
Testes para o script src/s03_csv_columns.py.
"""

import os
import sys
import pytest
from unittest.mock import patch

# Adiciona o diretório src ao sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from s03_csv_columns import check_csv_structures, main as columns_main

# --- Fixtures ---

@pytest.fixture
def temp_csv_dir(tmp_path):
    """Cria um diretório temporário com vários cenários de arquivos CSV."""
    data_dir = tmp_path / "data"
    data_dir.mkdir()

    # Arquivos consistentes
    (data_dir / "consistent1.csv").write_text("ID;Name;Value\n1;A;100", encoding="utf-8")
    (data_dir / "consistent2.csv").write_text("ID;Name;Value\n2;B;200", encoding="utf-8")

    # Arquivo com contagem de colunas diferente
    (data_dir / "diff_count.csv").write_text("ID;Name\n3;C", encoding="utf-8")

    # Arquivo com nomes/ordem de colunas diferentes
    (data_dir / "diff_order.csv").write_text("ID;Value;Name\n4;400;D", encoding="utf-8")

    # Arquivo vazio
    (data_dir / "empty.csv").touch()

    # Subdiretório com um arquivo consistente
    sub_dir = data_dir / "subdir"
    sub_dir.mkdir()
    (sub_dir / "consistent3.csv").write_text("ID;Name;Value\n5;E;500", encoding="utf-8")

    return data_dir

# --- Testes de Integração para check_csv_structures ---

def test_all_files_consistent(tmp_path):
    """Testa o cenário onde todos os arquivos são consistentes."""
    (tmp_path / "c1.csv").write_text("h1;h2\n1;2")
    (tmp_path / "c2.csv").write_text("h1;h2\n3;4")
    
    is_consistent, ref_header, inconsistent_files = check_csv_structures(str(tmp_path))
    
    assert is_consistent is True
    assert ref_header == ["h1", "h2"]
    assert not inconsistent_files

def test_inconsistent_files(temp_csv_dir):
    """Testa um mix de arquivos consistentes e inconsistentes."""
    is_consistent, ref_header, inconsistent_files = check_csv_structures(str(temp_csv_dir))
    
    assert is_consistent is False
    assert ref_header == ["ID", "Name", "Value"]
    assert len(inconsistent_files) == 3 # diff_count, diff_order, empty
    
    # Verifica as razões da inconsistência
    assert "Número de colunas diferente" in inconsistent_files["diff_count.csv"]
    assert "Diferença na coluna 2" in inconsistent_files["diff_order.csv"]
    assert "CSV vazio ou sem cabeçalho" in inconsistent_files["empty.csv"]

def test_no_csv_files_found(tmp_path):
    """Testa o comportamento quando nenhum arquivo CSV é encontrado."""
    is_consistent, ref_header, inconsistent_files = check_csv_structures(str(tmp_path))
    
    # O resultado deve ser "consistente" pois não há inconsistências a relatar
    assert is_consistent is True
    assert ref_header is None
    assert not inconsistent_files

@patch('s03_csv_columns.read_csv_robust', return_value=None)
def test_file_read_error(mock_read_csv, temp_csv_dir):
    """Testa o tratamento de erro quando a leitura de um arquivo falha."""
    # O mock fará com que a leitura de todos os arquivos falhe
    is_consistent, ref_header, inconsistent_files = check_csv_structures(str(temp_csv_dir))
    
    assert is_consistent is False
    assert ref_header is None # Nenhum cabeçalho de referência pode ser definido
    # Verifica se todos os arquivos encontrados foram marcados com erro
    assert len(inconsistent_files) > 0
    # Pega o primeiro item para verificar a mensagem de erro
    first_key = next(iter(inconsistent_files))
    assert "Falha na leitura" in inconsistent_files[first_key]

# --- Teste de Integração para o main ---

@patch('s03_csv_columns.check_csv_structures')
def test_main_function_call(mock_check, temp_csv_dir):
    """Testa se a função main invoca check_csv_structures com o diretório correto."""
    test_args = ["s03_csv_columns.py", "-d", str(temp_csv_dir)]
    
    with patch.object(sys, 'argv', test_args):
        columns_main()
        
    mock_check.assert_called_once_with(str(temp_csv_dir))

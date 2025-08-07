import os
import pandas as pd
import pytest
from unittest.mock import patch, MagicMock
import streamlit as st

# Adiciona o diretório raiz ao sys.path
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.app_main_interface import load_lookup_columns

@pytest.fixture
def temp_dir(tmp_path):
    """Cria um diretório temporário para os arquivos de teste."""
    return tmp_path

def test_load_lookup_columns_csv_success(temp_dir):
    """Testa o carregamento bem-sucedido de colunas de um arquivo CSV."""
    # Arrange
    project_path = str(temp_dir)
    lookup_file = "test.csv"
    file_path = os.path.join(project_path, lookup_file)
    df = pd.DataFrame({"col1": [1], "col2": [2]})
    df.to_csv(file_path, index=False, sep=';')

    # Act
    with patch('streamlit.warning') as mock_warning:
        columns = load_lookup_columns(project_path, lookup_file, delimiter=';')

    # Assert
    assert columns == ["col1", "col2"]
    mock_warning.assert_not_called()

def test_load_lookup_columns_xlsx_success(temp_dir):
    """Testa o carregamento bem-sucedido de colunas de um arquivo XLSX."""
    # Arrange
    project_path = str(temp_dir)
    lookup_file = "test.xlsx"
    file_path = os.path.join(project_path, lookup_file)
    df = pd.DataFrame({"colA": ["x"], "colB": ["y"]})
    df.to_excel(file_path, index=False)

    # Act
    with patch('streamlit.warning') as mock_warning:
        columns = load_lookup_columns(project_path, lookup_file)

    # Assert
    assert columns == ["colA", "colB"]
    mock_warning.assert_not_called()

def test_load_lookup_columns_file_not_found():
    """Testa o comportamento quando o arquivo de lookup não é encontrado."""
    # Arrange
    project_path = "non_existent_path"
    lookup_file = "non_existent_file.csv"

    # Act
    with patch('streamlit.warning') as mock_warning:
        columns = load_lookup_columns(project_path, lookup_file)

    # Assert
    assert columns == []
    mock_warning.assert_called_once_with(f"Arquivo de lookup não encontrado: {lookup_file}")

@patch('src.connectors.factory.get_data_loader')
def test_load_lookup_columns_read_error(mock_get_loader, temp_dir):
    """Testa o tratamento de erro quando a leitura do arquivo falha."""
    # Arrange
    project_path = str(temp_dir)
    lookup_file = "file_with_read_error.csv"
    file_path = os.path.join(project_path, lookup_file)
    with open(file_path, 'w') as f:
        f.write("dummy content")

    mock_connector = MagicMock()
    mock_connector.read.side_effect = Exception("Read error")
    mock_get_loader.return_value = mock_connector

    # Act
    columns = load_lookup_columns(project_path, lookup_file, delimiter=';')

    # Assert
    assert columns == []

def test_load_lookup_columns_empty_file(temp_dir):
    """Testa o comportamento com um arquivo vazio."""
    # Arrange
    project_path = str(temp_dir)
    lookup_file = "empty.csv"
    file_path = os.path.join(project_path, lookup_file)
    with open(file_path, 'w') as f:
        pass  # Cria um arquivo vazio

    # Act
    columns = load_lookup_columns(project_path, lookup_file)

    # Assert
    assert columns == []

def test_load_lookup_columns_no_columns(temp_dir):
    """Testa o comportamento com um arquivo que não tem colunas."""
    # Arrange
    project_path = str(temp_dir)
    lookup_file = "no_columns.csv"
    file_path = os.path.join(project_path, lookup_file)
    # Um CSV com uma linha em branco pode ser lido como um DF sem colunas
    with open(file_path, 'w') as f:
        f.write('\n')

    # Act
    columns = load_lookup_columns(project_path, lookup_file)

    # Assert
    assert columns == []

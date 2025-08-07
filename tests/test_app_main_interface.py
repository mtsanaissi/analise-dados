import os
import pandas as pd
import pytest
from unittest.mock import patch, MagicMock, mock_open
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

# Fixture para inicializar o st.session_state
@pytest.fixture(autouse=True)
def clear_session_state():
    st.session_state.clear()
    yield
    st.session_state.clear()

def test_find_report_path_success():
    """Testa se o caminho do relatório é encontrado corretamente."""
    output = "Algum log aqui...\nRelatório salvo em: /path/to/report.html\nMais logs..."
    from src.app_main_interface import find_report_path
    assert find_report_path(output) == "/path/to/report.html"

def test_find_report_path_failure():
    """Testa o que acontece quando o caminho do relatório não é encontrado."""
    output = "Nenhum relatório foi gerado."
    from src.app_main_interface import find_report_path
    assert find_report_path(output) is None

@patch('src.app_main_interface.build_command')
@patch('src.app_main_interface.run_process')
def test_command_is_stored_in_session_state(mock_run_process, mock_build_command):
    """Verifica se o comando executado é armazenado no st.session_state."""
    # Arrange
    from src.app_main_interface import main_interface
    mock_build_command.return_value = ["python", "run.py", "-d", "data/sample", "-p", "discovery"]
    mock_run_process.return_value = (0, "Execução de teste bem-sucedida.")
    st.session_state.running = True

    # Act
    main_interface()

    # Assert
    assert "last_command" in st.session_state
    assert st.session_state.last_command == ["python", "run.py", "-d", "data/sample", "-p", "discovery"]

@patch('src.app_main_interface.find_report_path')
@patch('streamlit.subheader')
@patch('streamlit.code')
def test_results_display_with_expander(mock_code, mock_subheader, mock_find_report):
    """Verifica se o st.expander é chamado para exibir os detalhes da execução."""
    # Arrange
    from src.app_main_interface import main_interface
    st.session_state.last_run_results = {
        "return_code": 0,
        "full_output": "Log de execução.",
        "selected_phase": "discovery"
    }
    st.session_state.last_command = ["comando", "de", "teste"]
    mock_find_report.return_value = None  # Simula que não há relatório

    # Act
    main_interface()

    # Assert
    from unittest.mock import call
    mock_subheader.assert_any_call("Comando Executado")
    mock_subheader.assert_any_call("Log de Saída")
    mock_code.assert_any_call("comando de teste", language='bash')
    mock_code.assert_any_call("Log de execução.", language='bash')

@patch('os.path.exists', return_value=True)
@patch('builtins.open', new_callable=mock_open, read_data='<html></html>')
@patch('streamlit.components.v1.html')
def test_html_report_is_displayed(mock_st_html, mock_file, mock_exists):
    """Verifica se um relatório HTML é renderizado corretamente."""
    # Arrange
    from src.app_main_interface import main_interface
    report_path = "/fake/path/report.html"
    st.session_state.last_run_results = {
        "return_code": 0,
        "full_output": f"Relatório salvo em: {report_path}",
        "selected_phase": "discovery"
    }
    st.session_state.last_command = ["fake", "command"]

    # Act
    main_interface()

    # Assert
    mock_st_html.assert_called_once_with('<html></html>', height=600, scrolling=True)

@patch('os.path.exists', return_value=True)
@patch('builtins.open', new_callable=mock_open, read_data='{"key": "value"}')
@patch('streamlit.json')
def test_json_report_is_displayed(mock_st_json, mock_file, mock_exists):
    """Verifica se um relatório JSON é renderizado corretamente."""
    # Arrange
    from src.app_main_interface import main_interface
    report_path = "/fake/path/report.json"
    st.session_state.last_run_results = {
        "return_code": 0,
        "full_output": f"Relatório salvo em: {report_path}",
        "selected_phase": "discovery"
    }
    st.session_state.last_command = ["fake", "command"]

    # Act
    main_interface()

    # Assert
    import json
    mock_st_json.assert_called_once_with(json.loads('{"key": "value"}'))

@patch('streamlit.error')
def test_error_message_is_shown_on_failure(mock_st_error):
    """Verifica se st.error é chamado quando a execução falha."""
    # Arrange
    from src.app_main_interface import main_interface
    st.session_state.last_run_results = {
        "return_code": 1,
        "full_output": "Houve um erro.",
        "selected_phase": "treatment"
    }
    st.session_state.last_command = ["bad", "command"]

    # Act
    main_interface()

    # Assert
    mock_st_error.assert_called_with("Ocorreu um erro durante a execução.")

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

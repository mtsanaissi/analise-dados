import os
import pandas as pd
import pytest
from unittest.mock import patch
import streamlit as st

# Importa as funções a serem testadas
from src.app_main_interface import load_lookup_columns, execute_run_logic

# Fixture para inicializar o st.session_state
@pytest.fixture(autouse=True)
def clear_session_state():
    st.session_state.clear()
    yield
    st.session_state.clear()

# ==================================================================
# Testes para load_lookup_columns (mantidos do original)
# ==================================================================
@pytest.fixture
def temp_dir(tmp_path):
    return tmp_path

def test_load_lookup_columns_csv_success(temp_dir):
    project_path = str(temp_dir)
    lookup_file = "test.csv"
    file_path = os.path.join(project_path, lookup_file)
    df = pd.DataFrame({"col1": [1], "col2": [2]})
    df.to_csv(file_path, index=False, sep=';')
    with patch('streamlit.warning') as mock_warning:
        columns = load_lookup_columns(project_path, lookup_file, delimiter=';')
    assert columns == ["col1", "col2"]
    mock_warning.assert_not_called()

# ==================================================================
# Novos Testes para a Lógica de Execução Refatorada
# ==================================================================

@patch('src.app_main_interface.run_discovery_logic')
@patch('streamlit.empty')
@patch('streamlit.spinner')
def test_execute_run_logic_discovery_success(mock_spinner, mock_empty, mock_run_discovery):
    """Testa uma execução bem-sucedida da fase de discovery através da nova função de lógica."""
    # Arrange
    mock_run_discovery.return_value = {"status": "success", "message": "Discovery OK", "report_path": "/fake/report.json"}
    discovery_args = {"report_output": "json", "compare_fields": True}

    # Act
    execute_run_logic("fake/path", "discovery", discovery_args, {})

    # Assert
    mock_run_discovery.assert_called_once_with(
        data_project_path="fake/path",
        report_output="json",
        compare_fields=True,
        compare_types=False,  # Verifica o default
        generate_char_cleanup_config=None
    )
    assert st.session_state.last_run_results['return_code'] == 0
    assert st.session_state.last_run_results['full_output'] == "Discovery OK"
    assert st.session_state.last_run_results['report_path'] == "/fake/report.json"

@patch('src.app_main_interface.run_treatment_dispatcher')
@patch('streamlit.empty')
@patch('streamlit.spinner')
def test_execute_run_logic_treatment_success(mock_spinner, mock_empty, mock_dispatcher):
    """Testa uma execução bem-sucedida da fase de treatment através da nova função de lógica."""
    # Arrange
    mock_dispatcher.return_value = {"status": "success", "message": "Treatment OK", "report_path": "/fake/output"}
    treatment_args = {"operation": "Remover Espaços"}

    # Act
    execute_run_logic("fake/path", "treatment", {}, treatment_args)

    # Assert
    mock_dispatcher.assert_called_once_with("fake/path", "Remover Espaços", None)
    assert st.session_state.last_run_results['return_code'] == 0
    assert st.session_state.last_run_results['full_output'] == "Treatment OK"

@patch('src.app_main_interface.run_discovery_logic', side_effect=Exception("Falha geral"))
@patch('streamlit.empty')
@patch('streamlit.spinner')
def test_execute_run_logic_exception_handling(mock_spinner, mock_empty, mock_run_discovery):
    """Verifica se exceções na lógica de negócios são capturadas corretamente."""
    # Arrange
    discovery_args = {"report_output": "json"}

    # Act
    execute_run_logic("fake/path", "discovery", discovery_args, {})

    # Assert
    assert st.session_state.last_run_results['return_code'] == 1
    assert "Falha geral" in st.session_state.last_run_results['full_output']
    assert st.session_state.last_run_results['report_path'] is None

@patch('streamlit.warning')
@patch('streamlit.empty')
@patch('streamlit.spinner')
def test_execute_run_logic_no_treatment_operation(mock_spinner, mock_empty, mock_warning):
    """Verifica o comportamento quando nenhuma operação de tratamento é selecionada."""
    # Arrange
    treatment_args = {"operation": "Selecione uma operação"}

    # Act
    execute_run_logic("fake/path", "treatment", {}, treatment_args)

    # Assert
    mock_warning.assert_called_with("Por favor, selecione uma operação de tratamento.")
    # Verifica se um resultado neutro foi definido
    assert st.session_state.last_run_results['full_output'] == "Nenhuma operação selecionada."

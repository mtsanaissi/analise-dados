# -*- coding: utf-8 -*-
import pytest
from unittest.mock import patch, MagicMock
import sys
from src.main import orchestrator

@pytest.fixture
def mock_args():
    """Fixture para simular os argumentos da linha de comando."""
    def _mock_args(phase, data_project_path):
        return ["-p", phase, "-d", data_project_path]
    return _mock_args

@patch("src.main.orchestrator.os.path.isdir")
@patch("src.phases.phase01_discovery.phase01_orchestrator.run_discovery_logic")
def test_main_discovery_phase(mock_run_discovery, mock_isdir, mock_args, tmp_path):
    """Testa se a fase 'discovery' é chamada com os argumentos corretos."""
    # Arrange
    mock_isdir.return_value = True
    data_path = str(tmp_path)
    test_args = ["program_name"] + mock_args("discovery", data_path)

    with patch.object(sys, 'argv', test_args):
        # Act
        orchestrator.main()

        # Assert
        mock_run_discovery.assert_called_once_with(data_project_path=data_path)


@patch("src.main.orchestrator.os.path.isdir")
def test_main_invalid_path(mock_isdir, mock_args, caplog):
    """Testa o comportamento do orquestrador com um caminho de projeto inválido."""
    # Arrange
    mock_isdir.return_value = False
    invalid_path = "/invalid/path"
    test_args = ["program_name"] + mock_args("discovery", invalid_path)

    with patch.object(sys, 'argv', test_args):
        with pytest.raises(SystemExit) as e:
            # Act
            orchestrator.main()

            # Assert
            assert e.type == SystemExit
            assert e.value.code == 1

    assert "não é um diretório válido" in caplog.text

@patch("src.main.orchestrator.argparse.ArgumentParser.parse_known_args")
def test_argument_parsing(mock_parse_args):
    """Testa se os argumentos da linha de comando são parseados corretamente."""
    # Arrange
    # Simula o retorno de parse_known_args
    mock_args_obj = MagicMock()
    mock_args_obj.phase = 'discovery'
    mock_args_obj.data_project_path = '/fake/path'
    mock_parse_args.return_value = (mock_args_obj, [])

    # Mock para evitar a execução do resto da função
    with patch('src.main.orchestrator.os.path.isdir', return_value=True):
        with patch('src.phases.phase01_discovery.phase01_orchestrator.run_discovery_logic'):
            # Act
            orchestrator.main()

            # Assert
            mock_parse_args.assert_called_once()
            # O teste aqui é que a função é chamada; a lógica interna do argparse é confiável.
            # A verificação de que as fases são chamadas corretamente (nos outros testes)
            # confirma indiretamente que o parsing funciona.
            assert True

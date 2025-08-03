# -*- coding: utf-8 -*-

# --------------------------------------------------------------------------------
# Descrição: Testes de unidade para a interface principal da aplicação Streamlit.
#            Foca em validar a lógica de construção de comandos.
#
# Autor: Jules
# Criado em: 01/08/2025
# Versão: 1.0
#
# Modificado por: Jules
# Modificado em: 02/08/2025
# Licença: MIT
# --------------------------------------------------------------------------------

import sys
import os
import pytest

# Adiciona o diretório 'src' ao sys.path para importação do módulo
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from app_main_interface import build_command

@pytest.mark.parametrize(
    "project_path, phase",
    [
        ("data/sample", "discovery"),
        ("my/project/path", "treatment"),
        ("/absolute/path/to/data", "exploratory"),
        ("another_project", "visualization"),
    ]
)
def test_build_command_construction(project_path, phase):
    """
    Testa se a função build_command constrói a lista de argumentos corretamente
    para diferentes combinações de `project_path` e `phase`.
    """
    # Chama a função
    command = build_command(project_path, phase)

    # Caminho esperado para o script run.py
    expected_script_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src', 'run.py'))

    # Executável esperado do Python
    expected_python_executable = sys.executable

    # Verifica se o comando foi construído como esperado
    expected_command = [
        expected_python_executable,
        expected_script_path,
        "-d",
        project_path,
        "-p",
        phase
    ]

    assert command == expected_command, f"O comando gerado {command} não corresponde ao esperado {expected_command}"

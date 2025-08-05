# -*- coding: utf-8 -*-

# --------------------------------------------------------------------------------
# Descrição: Interface principal do Streamlit para o kit de ferramentas de análise de dados.
#            Permite ao usuário selecionar a fase do projeto e o caminho dos dados,
#            executando o processo correspondente e exibindo a saída em tempo real.
# Exemplo de uso: streamlit run src/app_main_interface.py
#
# Autor: Jules
# Criado em: 01/08/2025
# Versão: 1.0
#
# Modificado por: -
# Modificado em: -
# Licença: MIT
# --------------------------------------------------------------------------------

import streamlit as st
import subprocess
import os
import sys
from typing import List

def build_command(project_path: str, phase: str) -> List[str]:
    """
    Constrói a lista de argumentos do comando para o subprocesso.

    Args:
        project_path (str): O caminho para o projeto de dados.
        phase (str): A fase do projeto a ser executada.

    Returns:
        List[str]: A lista de argumentos do comando.
    """
    # Garante que o executável do Python no ambiente virtual seja usado
    python_executable = sys.executable
    run_script_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'run.py'))

    command = [
        python_executable,
        run_script_path,
        "-d",
        project_path,
        "-p",
        phase
    ]
    return command

def run_process(command: List[str], output_placeholder):
    """
    Executa um comando em um subprocesso e exibe a saída em tempo real.

    Args:
        command (List[str]): O comando a ser executado.
        output_placeholder: O elemento Streamlit onde a saída será exibida.
    """
    process = None
    full_output = ""
    try:
        # Garante que o subprocesso use UTF-8 para stdout/stderr, crucial para Windows
        env = os.environ.copy()
        env["PYTHONIOENCODING"] = "utf-8"

        # Usar Popen para capturar a saída em tempo real
        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding='utf-8',
            errors='replace',
            bufsize=1,
            env=env
        )

        # Exibir a saída linha por linha
        for line in iter(process.stdout.readline, ''):
            full_output += line
            output_placeholder.code(full_output)

        process.stdout.close()
        return_code = process.wait()

        if return_code == 0:
            st.success("Execução concluída com sucesso!")
        else:
            st.error(f"Erro na execução. O processo terminou com o código: {return_code}")

    except FileNotFoundError:
        st.error(f"Erro: O comando '{command[0]}' não foi encontrado. Verifique se o Python está no PATH.")
        full_output += f"\nErro: O comando '{command[0]}' não foi encontrado."
    except Exception as e:
        st.error(f"Ocorreu um erro inesperado: {e}")
        full_output += f"\nOcorreu um erro inesperado: {e}"
    finally:
        # Garante que o processo seja finalizado se ainda estiver em execução
        if process and process.poll() is None:
            process.kill()


def main_interface():
    """
    Configura e exibe a interface principal do Streamlit.
    """
    st.set_page_config(layout="wide", page_title="Kit de Ferramentas de Análise de Dados")

    st.title("Painel de Controle do Kit de Ferramentas")

    # --- Barra Lateral ---
    with st.sidebar:
        st.header("Configurações de Execução")

        project_path = st.text_input(
            "Caminho do Projeto de Dados",
            "data/sample",
            help="Forneça o caminho para o diretório do projeto contendo os dados."
        )

        # As fases correspondem aos diretórios em `src/phases`
        phases = ["discovery", "treatment", "exploratory", "visualization"]
        selected_phase = st.selectbox(
            "Fase do Projeto",
            options=phases,
            help="Selecione a fase do projeto a ser executada."
        )

    # --- Área Principal ---
    if st.button("Executar", type="primary"):
        if not project_path:
            st.warning("Por favor, forneça o caminho do projeto de dados.")
        elif not os.path.isdir(project_path):
            st.error(f"O caminho '{project_path}' não é um diretório válido.")
        else:
            command = build_command(project_path, selected_phase)

            st.info(f"Executando comando: `{' '.join(command)}`")

            # Placeholder para a saída
            output_placeholder = st.empty()
            output_placeholder.code("Iniciando a execução...")

            run_process(command, output_placeholder)

if __name__ == "__main__":
    main_interface()

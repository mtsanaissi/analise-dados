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
import tempfile
from .utils import build_command

def run_process(command: list[str], output_placeholder):
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
        if process and process.poll() is None:
            process.kill()

def main_interface():
    """
    Configura e exibe a interface principal do Streamlit.
    """
    st.set_page_config(layout="wide", page_title="Kit de Ferramentas de Análise de Dados")
    st.title("Painel de Controle do Kit de Ferramentas")

    with st.sidebar:
        st.header("Configurações de Execução")
        project_path = st.text_input(
            "Caminho do Projeto de Dados",
            "data/sample",
            help="Forneça o caminho para o diretório do projeto contendo os dados."
        )
        phases = ["discovery", "treatment", "exploratory", "visualization"]
        selected_phase = st.selectbox(
            "Fase do Projeto",
            options=phases,
            help="Selecione a fase do projeto a ser executada."
        )

        discovery_args = {}
        treatment_args = {}

        if selected_phase == "discovery":
            with st.expander("Opções da Fase de Discovery", expanded=True):
                discovery_args["compare_fields"] = st.checkbox(
                    "Comparar Campos/Colunas",
                    help="Habilita a comparação de campos/colunas entre arquivos do mesmo tipo."
                )
                discovery_args["compare_types"] = st.checkbox(
                    "Comparar Tipos de Dados",
                    help="Habilita a comparação de tipos de dados entre colunas de mesmo nome."
                )
                discovery_args["report_output"] = st.selectbox(
                    "Formato do Relatório",
                    options=["json", "html"],
                    help="Selecione o formato do arquivo de relatório."
                )
                discovery_args["char_cleanup_path"] = st.text_input(
                    "Gerar Config. de Limpeza de Caracteres",
                    help="Opcional. Especifique um caminho de saída para o arquivo de configuração de limpeza (ex: cleanup.yaml)."
                )

        if selected_phase == "treatment":
            with st.expander("Opções da Fase de Treatment", expanded=True):
                operations = [
                    "Selecione uma operação",
                    "Remover Espaços",
                    "Substituir Valores",
                    "Encontrar e Substituir Texto",
                    "Concatenar Dados",
                    "Enriquecer Dados"
                ]
                treatment_args["operation"] = st.selectbox("Operação de Tratamento", options=operations)

                if treatment_args["operation"] in ["Substituir Valores", "Encontrar e Substituir Texto", "Concatenar Dados", "Enriquecer Dados"]:
                    uploaded_file = st.file_uploader(
                        "Carregar Arquivo de Configuração YAML",
                        type=['yaml', 'yml']
                    )
                    treatment_args["config_file"] = uploaded_file

    if st.button("Executar", type="primary"):
        if not project_path:
            st.warning("Por favor, forneça o caminho do projeto de dados.")
        elif not os.path.isdir(project_path):
            st.error(f"O caminho '{project_path}' não é um diretório válido.")
        else:
            # Lógica para lidar com o arquivo carregado
            if selected_phase == "treatment" and treatment_args.get("config_file"):
                with tempfile.NamedTemporaryFile(delete=False, suffix=".yaml", mode='wb') as tmp:
                    tmp.write(treatment_args["config_file"].getvalue())
                    treatment_args["config_file_path"] = tmp.name
                st.info(f"Arquivo de configuração salvo temporariamente em: {treatment_args['config_file_path']}")

            command = build_command(
                project_path,
                selected_phase,
                discovery_args=discovery_args,
                treatment_args=treatment_args
            )
            st.info(f"Executando comando: `{' '.join(command)}`")
            output_placeholder = st.empty()
            output_placeholder.code("Iniciando a execução...")
            run_process(command, output_placeholder)

if __name__ == "__main__":
    main_interface()
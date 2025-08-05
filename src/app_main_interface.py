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
import re
import tempfile
from src.utils import build_command


def run_process(command: list[str], output_placeholder):
    """
    Executa um comando em um subprocesso e exibe a saída em tempo real.

    Args:
        command (List[str]): O comando a ser executado.
        output_placeholder: O elemento Streamlit onde a saída será exibida.

    Returns:
        Tuple[int, str]: O código de retorno e a saída completa do processo.
    """
    process = None
    full_output = ""
    return_code = -1
    try:
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
    except FileNotFoundError:
        full_output += f"\nErro: O comando '{command[0]}' não foi encontrado. Verifique se o Python está no PATH."
    except Exception as e:
        full_output += f"\nOcorreu um erro inesperado: {e}"
    finally:
        if process and process.poll() is None:
            process.kill()
    return return_code, full_output


def find_report_path(output: str) -> str | None:
    """
    Encontra o caminho de um arquivo de relatório na saída do processo.

    Args:
        output (str): A saída do processo.

    Returns:
        str | None: O caminho do relatório, se encontrado.
    """
    match = re.search(r"Relatório salvo em: (.*)", output)
    if match:
        return match.group(1).strip()
    return None


def main_interface():
    st.set_page_config(
        layout="wide", page_title="Kit de Ferramentas de Análise de Dados")
    st.title("Painel de Controle do Kit de Ferramentas")

    st.info(f"DEBUG: st.session_state = {st.session_state}")

    # Inicialização do estado da sessão
    if 'running' not in st.session_state:
        st.session_state.running = False
    if 'last_run_results' not in st.session_state:
        st.session_state.last_run_results = None

    with st.sidebar:
        st.header("Configurações de Execução")
        project_path = st.text_input(
            "Caminho do Projeto de Dados",
            "data/sample",
            help="Forneça o caminho para o diretório do projeto contendo os dados.",
            disabled=st.session_state.running
        )
        phases = ["discovery", "treatment"]
        selected_phase = st.selectbox(
            "Fase do Projeto",
            options=phases,
            help="Selecione a fase do projeto a ser executada.",
            disabled=st.session_state.running
        )

        discovery_args = {}
        treatment_args = {}

        if selected_phase == "discovery":
            with st.expander("Opções da Fase de Discovery", expanded=True):
                discovery_args["compare_fields"] = st.checkbox(
                    "Comparar Campos/Colunas", help="Habilita a comparação de campos/colunas.", disabled=st.session_state.running)
                discovery_args["compare_types"] = st.checkbox(
                    "Comparar Tipos de Dados", help="Habilita a comparação de tipos de dados.", disabled=st.session_state.running)
                discovery_args["report_output"] = st.selectbox("Formato do Relatório", options=[
                                                               "json", "html"], help="Selecione o formato do relatório.", disabled=st.session_state.running)
                discovery_args["char_cleanup_path"] = st.text_input(
                    "Gerar Config. de Limpeza", help="Opcional. Especifique um caminho para o arquivo de configuração de limpeza.", disabled=st.session_state.running)

        if selected_phase == "treatment":
            with st.expander("Opções da Fase de Treatment", expanded=True):
                operations = ["Selecione uma operação", "Remover Espaços", "Substituir Valores",
                              "Encontrar e Substituir Texto", "Concatenar Dados", "Enriquecer Dados"]
                treatment_args["operation"] = st.selectbox(
                    "Operação de Tratamento", options=operations, help="Selecione a operação de tratamento.", disabled=st.session_state.running)
                if treatment_args["operation"] in ["Substituir Valores", "Encontrar e Substituir Texto", "Concatenar Dados", "Enriquecer Dados"]:
                    treatment_args["config_file"] = st.file_uploader("Carregar Arquivo de Configuração YAML", type=[
                                                                     'yaml', 'yml'], help="Faça o upload do arquivo de configuração YAML.", disabled=st.session_state.running)

    # Lógica do botão de execução
    button_label = "Nova Execução" if st.session_state.last_run_results else "Executar"
    if st.sidebar.button(button_label, type="primary", use_container_width=True, disabled=st.session_state.running):
        st.info("Botão Executar clicado!")
        if not project_path or not os.path.isdir(project_path):
            st.error(f"O caminho '{project_path}' não é um diretório válido.")
        else:
            st.session_state.last_run_results = None
            st.session_state.running = True
            st.rerun()

    # Lógica de execução do processo
    if st.session_state.running:
        temp_config_path = None
        try:
            if selected_phase == "treatment" and treatment_args.get("config_file"):
                uploaded_file = treatment_args["config_file"]
                content_bytes = uploaded_file.getvalue()

                # Detecta a codificação do arquivo original
                detected_encoding = chardet.detect(content_bytes)['encoding']
                if not detected_encoding:
                    detected_encoding = 'utf-8'  # Padrão se a detecção falhar

                # Decodifica o conteúdo para uma string Python
                decoded_content = content_bytes.decode(detected_encoding)

                # Cria um arquivo temporário e escreve o conteúdo decodificado como UTF-8
                with tempfile.NamedTemporaryFile(delete=False, suffix=f"_{uploaded_file.name}", mode='w', encoding='utf-8') as tmp:
                    temp_config_path = tmp.name
                    tmp.write(decoded_content)

                treatment_args["config_file_path"] = temp_config_path

            command = build_command(
                project_path, selected_phase, discovery_args=discovery_args, treatment_args=treatment_args)
            st.info(f"Executando comando: `{' '.join(command)}`")
            output_placeholder = st.empty()
            output_placeholder.code("Iniciando a execução...")

            with st.spinner("Processando... Por favor, aguarde."):
                return_code, full_output = run_process(
                    command, output_placeholder)

            st.session_state.last_run_results = {
                "return_code": return_code, "full_output": full_output, "selected_phase": selected_phase}
        finally:
            if temp_config_path and os.path.exists(temp_config_path):
                os.remove(temp_config_path)
            st.session_state.running = False
            st.rerun()

    # Exibição dos resultados da última execução
    if st.session_state.last_run_results:
        results = st.session_state.last_run_results
        return_code = results["return_code"]
        full_output = results["full_output"]
        selected_phase = results["selected_phase"]

        if return_code == 0:
            st.success(f"Fase '{selected_phase}' concluída com sucesso!")
            report_path = find_report_path(full_output)
            if report_path and os.path.exists(report_path):
                with open(report_path, "rb") as f:
                    st.download_button(label="Baixar Relatório", data=f, file_name=os.path.basename(
                        report_path), use_container_width=True)
        else:
            st.error("Ocorreu um erro durante a execução.")

        st.code(full_output, language='bash')


if __name__ == "__main__":
    main_interface()

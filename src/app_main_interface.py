# -*- coding: utf-8 -*-

# --------------------------------------------------------------------------------
# Descrição: Interface principal do Streamlit para o kit de ferramentas de análise de dados.
#            Permite ao usuário selecionar a fase do projeto e o caminho dos dados,
#            executando o processo correspondente e exibindo a saída em tempo real.
# Exemplo de uso: streamlit run app.py
#
# Autor: Jules
# Criado em: 01/08/2025
# Versão: 1.0
#
# Modificado por: Jules
# Modificado em: 23/03/2026
# Licença: MIT
# --------------------------------------------------------------------------------

import os
import tempfile
import chardet
import json
import yaml
import streamlit as st

from src.utils import find_files
from src.connectors.factory import get_data_loader
from src.phases.phase01_discovery.phase01_orchestrator import run_discovery_logic
from src.phases.phase02_treatment.core.whitespace_remover import remove_whitespace
from src.phases.phase02_treatment.core.value_corrector import correct_values
from src.phases.phase02_treatment.core.text_replacer import replace_text
from src.phases.phase02_treatment.core.data_concatenator import concatenate_data
from src.phases.phase02_treatment.core.data_enricher import enrich_data
from typing import Dict, Any

def load_lookup_columns(project_path: str, lookup_file: str, delimiter: str = None) -> list:
    """Carrega as colunas de um arquivo de lookup."""
    if not lookup_file or not project_path:
        return []
    try:
        file_path = os.path.join(project_path, lookup_file)
        if not os.path.exists(file_path) and os.path.exists(lookup_file):
            file_path = lookup_file
        elif not os.path.exists(file_path):
            st.warning(f"Arquivo de lookup não encontrado: {lookup_file}")
            return []

        connector = get_data_loader(file_path, delimiter=delimiter)
        df = connector.read()
        return df.columns.tolist() if df is not None and not df.empty else []
    except Exception as e:
        st.error(f"Erro ao carregar colunas do arquivo de lookup: {e}")
        return []

def execute_run_logic(project_path: str, selected_phase: str, discovery_args: Dict[str, Any], treatment_args: Dict[str, Any]):
    """
    Executa a lógica de negócios principal com base na fase e nos argumentos selecionados.
    Esta função é separada para facilitar os testes.
    """
    output_placeholder = st.empty()
    output_placeholder.code("Iniciando a execução...")
    results = {}
    st.session_state.last_command = "N/A (Chamada Direta)"

    try:
        with st.spinner(f"Executando a fase de {selected_phase}... Por favor, aguarde."):
            if selected_phase == "discovery":
                cleanup_path = discovery_args.get("char_cleanup_path")
                results = run_discovery_logic(
                    data_project_path=project_path,
                    report_output=discovery_args.get("report_output", "json"),
                    compare_fields=discovery_args.get("compare_fields", False),
                    compare_types=discovery_args.get("compare_types", False),
                    generate_char_cleanup_config=cleanup_path if cleanup_path and cleanup_path.strip() else None
                )
            elif selected_phase == "treatment":
                operation = treatment_args.get("operation")
                if not operation or operation == "Selecione uma operação":
                    st.warning("Por favor, selecione uma operação de tratamento.")
                    # Define um resultado neutro para não quebrar a lógica de exibição
                    results = {"status": "warning", "message": "Nenhuma operação selecionada."}
                else:
                    config_data = None
                    if st.session_state.get('temp_config_path'):
                        with open(st.session_state.temp_config_path, 'r', encoding='utf-8') as f:
                            config_data = yaml.safe_load(f)

                    # Lógica do dispatcher de tratamento
                    results = run_treatment_dispatcher(project_path, operation, config_data)

            output_placeholder.code(results.get("message", "Operação concluída."))

    except Exception as e:
        results = {"status": "error", "message": str(e), "report_path": None}
        output_placeholder.code(f"Ocorreu um erro inesperado: {e}")

    # Armazena os resultados no estado da sessão
    st.session_state.last_run_results = {
        "return_code": 0 if results.get("status") == "success" else 1,
        "full_output": results.get("message", ""),
        "selected_phase": selected_phase,
        "report_path": results.get("report_path")
    }

def run_treatment_dispatcher(project_path: str, operation: str, config_data: Dict[str, Any]) -> Dict[str, Any]:
    """Executa a operação de tratamento apropriada."""

    if operation == "Remover Espaços":
        files_to_process = find_files(project_path, ['csv'])
        if not files_to_process:
            return {"status": "success", "message": "Nenhum arquivo CSV encontrado para processar."}

        output_dir = os.path.join(project_path, "fad-t-remocao-espacos")
        os.makedirs(output_dir, exist_ok=True)
        messages = [f"{os.path.basename(f)}: {remove_whitespace(input_file=f, output_file=os.path.join(output_dir, os.path.basename(f)))['message']}" for f in files_to_process]
        return {"status": "success", "message": "\n".join(messages), "report_path": output_dir}

    elif operation in ["Substituir Valores", "Encontrar e Substituir Texto", "Concatenar Dados"]:
        if not config_data:
            raise ValueError(f"Arquivo de configuração YAML é necessário para a operação '{operation}'.")

        if operation == "Substituir Valores":
            key, func, out_dir = 'corrections', correct_values, "fad-t-substituir-valores"
        elif operation == "Encontrar e Substituir Texto":
            key, func, out_dir = 'replacements', replace_text, "fad-t-substituir-texto"
        elif operation == "Concatenar Dados":
            output_filename = config_data.get('output_file')
            file_type = config_data.get('file_type', 'csv')
            if not output_filename: raise ValueError("A chave 'output_file' não foi encontrada.")
            output_path = os.path.join(project_path, output_filename)
            return concatenate_data(input_folder=project_path, output_file=output_path, file_type=file_type)

        config_list = config_data.get(key)
        if not config_list: raise ValueError(f"A chave '{key}' não foi encontrada no arquivo de configuração.")

        files_to_process = find_files(project_path, ['csv'])
        output_dir_path = os.path.join(project_path, out_dir)
        os.makedirs(output_dir_path, exist_ok=True)
        messages = [f"{os.path.basename(f)}: {func(input_file=f, output_file=os.path.join(output_dir_path, os.path.basename(f)), **{key: config_list})['message']}" for f in files_to_process]
        return {"status": "success", "message": "\n".join(messages), "report_path": output_dir_path}

    elif operation == "Enriquecer Dados":
        main_file = os.path.join(project_path, st.session_state.get('enrich_main_file', ''))
        lookup_file = st.session_state.get('enrich_lookup_file', '')
        if not os.path.isabs(lookup_file):
            lookup_file = os.path.join(project_path, lookup_file)

        if not os.path.exists(main_file): raise FileNotFoundError(f"Arquivo principal não encontrado: {main_file}")
        if not os.path.exists(lookup_file): raise FileNotFoundError(f"Arquivo de lookup não encontrado: {lookup_file}")

        output_dir = os.path.join(project_path, "fad-t-enriquecimento")
        os.makedirs(output_dir, exist_ok=True)
        output_file = os.path.join(output_dir, os.path.basename(main_file))

        return enrich_data(
            main_file=main_file, lookup_file=lookup_file,
            main_key=st.session_state.get('enrich_main_key'),
            lookup_key=st.session_state.get('enrich_lookup_key'),
            columns_to_add=st.session_state.get('enrich_columns_to_add'),
            output_file=output_file
        )

    return {"status": "error", "message": f"Operação '{operation}' não implementada."}

def main() -> None:
    """
    Inicializa e renderiza a interface principal do Streamlit.

    Args:
        None: Esta função não recebe argumentos.

    Returns:
        None: Esta função controla apenas o fluxo da interface.
    """
    st.set_page_config(layout="wide", page_title="Kit de Ferramentas de Análise de Dados")
    st.title("Painel de Controle do Kit de Ferramentas")

    if 'running' not in st.session_state:
        st.session_state.running = False
    if 'last_run_results' not in st.session_state:
        st.session_state.last_run_results = None
    if 'temp_config_path' not in st.session_state:
        st.session_state.temp_config_path = None

    with st.sidebar:
        st.header("Configurações de Execução")
        project_path = st.text_input("Caminho do Projeto de Dados", "data/sample", disabled=st.session_state.running)
        selected_phase = st.selectbox("Fase do Projeto", ["discovery", "treatment"], disabled=st.session_state.running)

        discovery_args = {}
        treatment_args = {}

        if selected_phase == "discovery":
            with st.expander("Opções da Fase de Discovery", expanded=True):
                discovery_args["compare_fields"] = st.checkbox("Comparar Campos/Colunas", disabled=st.session_state.running)
                discovery_args["compare_types"] = st.checkbox("Comparar Tipos de Dados", disabled=st.session_state.running)
                discovery_args["report_output"] = st.selectbox("Formato do Relatório", ["json", "html"], disabled=st.session_state.running)
                discovery_args["char_cleanup_path"] = st.text_input("Gerar Config. de Limpeza", disabled=st.session_state.running)

        if selected_phase == "treatment":
            with st.expander("Opções da Fase de Treatment", expanded=True):
                operations = ["Selecione uma operação", "Remover Espaços", "Substituir Valores",
                              "Encontrar e Substituir Texto", "Concatenar Dados", "Enriquecer Dados"]
                treatment_args["operation"] = st.selectbox("Operação de Tratamento", operations, disabled=st.session_state.running)

                if treatment_args["operation"] == "Enriquecer Dados":
                    st.subheader("Configuração de Enriquecimento")

                    if 'enrich_main_file' not in st.session_state: st.session_state.enrich_main_file = ''
                    if 'enrich_lookup_file' not in st.session_state: st.session_state.enrich_lookup_file = ''
                    if 'enrich_main_key' not in st.session_state: st.session_state.enrich_main_key = ''
                    if 'enrich_lookup_key' not in st.session_state: st.session_state.enrich_lookup_key = ''
                    if 'enrich_columns_to_add' not in st.session_state: st.session_state.enrich_columns_to_add = []
                    if 'lookup_columns' not in st.session_state: st.session_state.lookup_columns = []

                    main_file = st.text_input("Arquivo Principal", value=st.session_state.enrich_main_file, help="Nome do arquivo principal a ser enriquecido (ex: `vendas.csv`).", disabled=st.session_state.running)
                    lookup_file = st.text_input("Arquivo de Lookup", value=st.session_state.enrich_lookup_file, help="Caminho para o arquivo de lookup (ex: `produtos.xlsx`).", disabled=st.session_state.running)

                    if lookup_file and lookup_file != st.session_state.get('last_lookup_file'):
                        st.session_state.lookup_columns = load_lookup_columns(project_path, lookup_file)
                        st.session_state.last_lookup_file = lookup_file

                    main_key = st.text_input("Chave no Principal", value=st.session_state.enrich_main_key, help="Nome da coluna chave no arquivo principal.", disabled=st.session_state.running)
                    lookup_key = st.text_input("Chave no Lookup", value=st.session_state.enrich_lookup_key, help="Nome da coluna chave no arquivo de lookup.", disabled=st.session_state.running)
                    columns_to_add = st.multiselect("Colunas a Adicionar", options=st.session_state.lookup_columns, default=st.session_state.enrich_columns_to_add, help="Selecione as colunas do arquivo de lookup para adicionar ao principal.", disabled=st.session_state.running)

                    st.session_state.enrich_main_file = main_file
                    st.session_state.enrich_lookup_file = lookup_file
                    st.session_state.enrich_main_key = main_key
                    st.session_state.enrich_lookup_key = lookup_key
                    st.session_state.enrich_columns_to_add = columns_to_add
                elif treatment_args["operation"] in ["Substituir Valores", "Encontrar e Substituir Texto", "Concatenar Dados"]:
                    uploaded_file = st.file_uploader("Carregar Arquivo de Configuração YAML", type=['yaml', 'yml'], disabled=st.session_state.running)
                    if uploaded_file is not None and st.session_state.temp_config_path is None:
                        with tempfile.NamedTemporaryFile(delete=False, suffix=f"_{uploaded_file.name}", mode='w', encoding='utf-8') as tmp:
                            tmp.write(uploaded_file.getvalue().decode(chardet.detect(uploaded_file.getvalue())['encoding'] or 'utf-8'))
                            st.session_state.temp_config_path = tmp.name
                        st.rerun()

        if st.sidebar.button("Executar", type="primary", use_container_width=True, disabled=st.session_state.running):
            if not project_path or not os.path.isdir(project_path):
                st.error(f"O caminho '{project_path}' não é um diretório válido.")
            else:
                st.session_state.running = True
                st.rerun()

        if st.sidebar.button("Limpar Resultados", use_container_width=True, disabled=st.session_state.running):
            if st.session_state.temp_config_path and os.path.exists(st.session_state.temp_config_path):
                os.remove(st.session_state.temp_config_path)
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()

    if st.session_state.running:
        try:
            execute_run_logic(project_path, selected_phase, discovery_args, treatment_args)
        finally:
            st.session_state.running = False
            st.rerun()

    if st.session_state.get('last_run_results'):
        results = st.session_state.last_run_results
        st.subheader("Resultados da Execução")
        if results.get("return_code") == 0:
            st.success(f"Fase '{results.get('selected_phase')}' concluída com sucesso!")
        else:
            st.error("Ocorreu um erro durante a execução.")

        with st.expander("Ver Detalhes da Execução"):
            st.subheader("Log de Saída")
            st.code(results.get("full_output", ""), language='bash')

        report_path = results.get("report_path")
        if report_path and os.path.exists(report_path):
            st.subheader("Visualizador de Relatório")
            try:
                if report_path.endswith('.html'):
                    with open(report_path, 'r', encoding='utf-8') as f:
                        st.components.v1.html(f.read(), height=600, scrolling=True)
                elif report_path.endswith('.json'):
                    with open(report_path, 'r', encoding='utf-8') as f:
                        st.json(json.load(f))

                with open(report_path, "rb") as f:
                    st.download_button("Baixar Relatório", f, os.path.basename(report_path), use_container_width=True)
            except Exception as e:
                st.error(f"Erro ao ler ou exibir o arquivo de relatório: {e}")

def main_interface() -> None:
    """
    Mantém compatibilidade nominal com chamadas antigas da interface.

    Args:
        None: Esta função não recebe argumentos.

    Returns:
        None: Esta função delega para o entrypoint principal da interface.
    """
    main()


if __name__ == "__main__":
    main()

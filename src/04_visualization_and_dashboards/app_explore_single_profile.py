# -*- coding: utf-8 -*-

# --------------------------------------------------------------------------------
# Descrição: Uma aplicação web com Streamlit para explorar dinamicamente
#            conjuntos de dados usando ydata-profiling.
# Exemplo de uso: python app_explore_single_profile.py --argumento valor
#
# Autor: Marcelo Anaissi
# Criado em: 29/05/2025
# Versão: 1.1
#
# Modificado por: Jules
# Modificado em: 21/07/2025
# Licença: MIT
# --------------------------------------------------------------------------------

import os
import streamlit as st
import pandas as pd
from ydata_profiling import ProfileReport
from utils import find_files, read_csv_robust

# Cache para evitar recarregar e reprocessar os mesmos dados


@st.cache_data
def load_dataframe(file_path, delimiter):
    """Carrega um arquivo de dados em um DataFrame do Pandas."""
    if file_path.lower().endswith('.csv'):
        return read_csv_robust(file_path, delimiter=delimiter)
    elif file_path.lower().endswith(('.xlsx', '.xls')):
        # Por padrão, lê a primeira planilha. Poderíamos adicionar um seletor de planilhas.
        return pd.read_excel(file_path, sheet_name=0)
    elif file_path.lower().endswith('.json'):
        return pd.read_json(file_path)
    return None


@st.cache_data
def generate_profile_report(df, title):
    """Gera o relatório do ydata-profiling."""
    return ProfileReport(df, title=title, explorative=True)


# --- Interface da Aplicação ---
st.set_page_config(page_title="Explorador de Dados", layout="wide")

st.title("📊 Explorador de Perfil de Dados")
st.write("Use esta ferramenta para gerar e visualizar relatórios de perfilamento de dados de forma interativa.")

# --- Barra Lateral de Configuração ---
with st.sidebar:
    st.header("1. Configuração da Busca")

    # Use um caminho padrão sensato, o usuário pode alterar
    default_path = os.path.abspath(
        "../data/corrected") if os.path.exists("../data/corrected") else os.path.abspath(".")
    root_directory = st.text_input(
        "Diretório Raiz dos Dados", value=default_path)

    include_subdirs = st.checkbox("Incluir Subdiretórios", value=True)

    extensions = st.multiselect(
        "Extensões de Arquivo",
        options=['csv', 'xlsx', 'xls', 'json', 'parquet'],
        default=['csv', 'xlsx']
    )

    delimiter = st.text_input("Delimitador CSV", value=";")

    if 'file_list' not in st.session_state:
        st.session_state.file_list = []

    if st.button("Buscar Arquivos"):
        with st.spinner("Buscando arquivos..."):
            if os.path.isdir(root_directory):
                st.session_state.file_list = find_data_files(
                    root_directory, extensions, include_subdirs)
                if not st.session_state.file_list:
                    st.warning(
                        "Nenhum arquivo encontrado com os critérios especificados.")
                else:
                    st.success(
                        f"Encontrados {len(st.session_state.file_list)} arquivos!")
            else:
                st.error("O diretório especificado não existe.")
                st.session_state.file_list = []

# --- Área Principal da Aplicação ---
if st.session_state.file_list:
    st.header("2. Selecione um Arquivo para Análise")

    # Criamos um dicionário para exibir nomes de arquivo mais amigáveis no selectbox
    # e ainda manter o caminho completo
    file_options = {os.path.relpath(
        f, root_directory): f for f in st.session_state.file_list}

    selected_file_display = st.selectbox(
        "Arquivos Encontrados:",
        options=list(file_options.keys()),
        index=0,
        # Adiciona um ícone para ficar mais bonito
        format_func=lambda x: f"📄 {x}"
    )

    if selected_file_display:
        selected_file_path = file_options[selected_file_display]
        st.info(
            f"Caminho completo do arquivo selecionado: `{selected_file_path}`")

        st.header("3. Relatório de Perfilamento")

        with st.spinner(f"Carregando e analisando '{selected_file_display}'... Por favor, aguarde."):
            try:
                df = load_dataframe(selected_file_path,
                                    delimiter.replace('\\t', '\t'))

                if df is not None:
                    # Gera o relatório
                    profile = generate_profile_report(
                        df, title=f"Relatório de Análise para {selected_file_display}")

                    # Converte o relatório para HTML
                    report_html = profile.to_html()

                    # Exibe o HTML no Streamlit
                    st.components.v1.html(
                        report_html, height=800, scrolling=True)
                else:
                    st.error(
                        "Não foi possível carregar ou tipo de arquivo não suportado.")
            except Exception as e:
                st.error(f"Ocorreu um erro ao processar o arquivo: {e}")
else:
    st.info("⬅️ Configure os parâmetros de busca na barra lateral e clique em 'Buscar Arquivos' para começar.")

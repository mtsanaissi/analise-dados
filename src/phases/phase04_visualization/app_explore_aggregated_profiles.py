# -*- coding: utf-8 -*-

# --------------------------------------------------------------------------------
# Descrição: Uma aplicação web com Streamlit para explorar dinamicamente
#            o perfil de dados de forma individual (por arquivo),
#            agregada por ano, ou do conjunto de dados completo.
# Exemplo de uso: python app_explore_aggregated_profiles.py --argumento valor
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
import re
import streamlit as st
import pandas as pd
from ydata_profiling import ProfileReport
from src.utils import find_files, read_csv_robust

# --- Funções de Lógica de Dados ---

def find_and_parse_files(root_path, recursive):
    """
    Encontra todos os arquivos CSV e extrai o ano de seus caminhos.
    Retorna uma lista de tuplas (caminho_completo, ano).
    """
    all_csv_files = find_files(root_path, ['csv'], recursive)
    parsed_files = []
    year_month_regex = re.compile(r'(\d{4})-(\d{2})')

    for file_path in all_csv_files:
        match = year_month_regex.search(file_path)
        if match:
            year = int(match.group(1))
            parsed_files.append((file_path, year))

    return parsed_files

def filter_files_by_year(parsed_files, selected_year):
    """
    Filtra a lista de arquivos para um ano específico.
    """
    return [path for path, year in parsed_files if year == selected_year]

def load_and_concat_data(files_to_load, delimiter):
    """
    Carrega múltiplos arquivos CSV e os concatena em um único DataFrame.
    """
    df_list = []
    for file_path in files_to_load:
        try:
            df = read_csv_robust(file_path, delimiter=delimiter)
            if df is not None:
                df_list.append(df)
        except Exception as e:
            st.warning(f"Não foi possível carregar o arquivo '{os.path.basename(file_path)}': {e}")
            continue

    if not df_list:
        return None
    return pd.concat(df_list, ignore_index=True)

def generate_profile_report(df, title):
    """
    Gera o relatório do ydata-profiling.
    """
    return ProfileReport(df, title=title, explorative=True, minimal=False)


# --- Interface da Aplicação ---
def run_app():
    st.set_page_config(page_title="Análise de Dados Agregada", layout="wide")
    st.title("📊 Análise de Perfil de Dados (Individual e Agregada)")
    st.write("Selecione um modo de análise para gerar relatórios de perfilamento para um arquivo, um ano inteiro, ou todo o conjunto de dados.")

    # --- Barra Lateral de Configuração ---
    with st.sidebar:
        st.header("1. Configuração da Fonte de Dados")
        default_path = os.path.abspath("./data")
        root_directory = st.text_input("Diretório Raiz dos Dados", value=default_path)
        include_subdirs = st.checkbox("Buscar em Subdiretórios", value=True)
        delimiter = st.text_input("Delimitador CSV", value=";")

        if st.button("Carregar e Analisar Dados"):
            with st.spinner("Buscando e processando informações dos arquivos..."):
                if os.path.isdir(root_directory):
                    st.session_state.parsed_files = find_and_parse_files(root_directory, include_subdirs)
                    if not st.session_state.parsed_files:
                        st.warning("Nenhum arquivo CSV com formato AAAA-MM foi encontrado.")
                    else:
                        st.session_state.data_loaded = True
                        st.success(f"Encontrados {len(st.session_state.parsed_files)} arquivos relevantes.")
                else:
                    st.error("O diretório especificado não existe.")
                    st.session_state.data_loaded = False

    if 'data_loaded' not in st.session_state:
        st.session_state.data_loaded = False

    # --- Área Principal da Aplicação ---
    if not st.session_state.data_loaded:
        st.info("⬅️ Configure o diretório de dados na barra lateral e clique em 'Carregar e Analisar Dados' para começar.")
    else:
        st.header("2. Modo de Análise")
        analysis_mode = st.radio("Escolha como deseja analisar os dados:",
                                 ("Por Arquivo", "Por Ano", "Conjunto Completo"), horizontal=True)

        files_to_process = []
        report_title = ""

        if analysis_mode == "Por Arquivo":
            st.subheader("Análise por Arquivo Individual")
            file_options = {os.path.relpath(path, root_directory): path for path, year in st.session_state.parsed_files}
            selected_display = st.selectbox("Selecione um arquivo:", list(file_options.keys()))
            if selected_display:
                files_to_process = [file_options[selected_display]]
                report_title = f"Relatório de Análise para o Arquivo: {selected_display}"

        elif analysis_mode == "Por Ano":
            st.subheader("Análise Agregada por Ano")
            available_years = sorted(list(set(year for path, year in st.session_state.parsed_files)), reverse=True)
            selected_year = st.selectbox("Selecione um ano:", available_years)
            if selected_year:
                files_to_process = filter_files_by_year(st.session_state.parsed_files, selected_year)
                report_title = f"Relatório de Análise Agregado para o Ano: {selected_year}"
                st.write(f"Serão concatenados {len(files_to_process)} arquivos para o ano de {selected_year}.")

        elif analysis_mode == "Conjunto Completo":
            st.subheader("Análise do Conjunto de Dados Completo")
            files_to_process = [path for path, year in st.session_state.parsed_files]
            report_title = "Relatório de Análise para o Conjunto de Dados Completo"
            st.write(f"Serão concatenados todos os {len(files_to_process)} arquivos encontrados.")

        if files_to_process:
            st.header("3. Relatório de Perfilamento")
            with st.spinner(f"Processando... Isto pode levar alguns minutos, especialmente para análises agregadas."):
                try:
                    df_aggregated = load_and_concat_data(files_to_process, delimiter.replace('\\t', '\t'))
                    if df_aggregated is not None and not df_aggregated.empty:
                        profile = generate_profile_report(df_aggregated, title=report_title)
                        report_html = profile.to_html()
                        st.components.v1.html(report_html, height=800, scrolling=True)
                    else:
                        st.error("Não foi possível carregar dados para a seleção atual.")
                except Exception as e:
                    st.error(f"Ocorreu um erro ao gerar o relatório: {e}")

if __name__ == "__main__":
    run_app()

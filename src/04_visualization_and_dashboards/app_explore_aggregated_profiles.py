#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ----------------------------------------------------------------------------
# Script: explore_aggregated_profiles_app.py
# Autor: Seu Nome/Empresa
# Data: DD/MM/AAAA
# Versão: 1.0
# Descrição: Uma aplicação web com Streamlit para explorar dinamicamente
#            o perfil de dados de forma individual (por arquivo),
#            agregada por ano, ou do conjunto de dados completo.
# ----------------------------------------------------------------------------

import os
import re
import streamlit as st
import pandas as pd
from ydata_profiling import ProfileReport
from ..utils import find_files, read_csv_robust

# --- Funções Auxiliares ---


@st.cache_data
def find_and_parse_files(root_path, recursive):
    """
    Encontra todos os arquivos CSV e extrai o ano de seus caminhos.
    Retorna uma lista de tuplas (caminho_completo, ano).
    """
    all_csv_files = find_files(root_path, ['csv'], recursive)

    parsed_files = []
    # Expressão regular para encontrar 'AAAA-MM' no caminho do arquivo
    year_month_regex = re.compile(r'(\d{4})-(\d{2})')

    for file_path in all_csv_files:
        match = year_month_regex.search(file_path)
        if match:
            year = int(match.group(1))
            parsed_files.append((file_path, year))

    return parsed_files


@st.cache_data
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
            # Em uma aplicação real, seria bom logar isso
            st.warning(
                f"Não foi possível carregar o arquivo '{os.path.basename(file_path)}': {e}")
            continue

    if not df_list:
        return None

    # Concatena todos os dataframes da lista
    return pd.concat(df_list, ignore_index=True)


@st.cache_data
def generate_profile_report(_df, title):
    """
    Gera o relatório do ydata-profiling. O _df é para o cache do Streamlit.
    """
    return ProfileReport(_df, title=title, explorative=True, minimal=False)


# --- Interface da Aplicação ---
st.set_page_config(page_title="Análise de Dados Agregada", layout="wide")

st.title("📊 Análise de Perfil de Dados (Individual e Agregada)")
st.write("Selecione um modo de análise para gerar relatórios de perfilamento para um arquivo, um ano inteiro, ou todo o conjunto de dados.")

# --- Barra Lateral de Configuração ---
with st.sidebar:
    st.header("1. Configuração da Fonte de Dados")

    default_path = os.path.abspath("../data")  # Aponta para o diretório 'data'
    root_directory = st.text_input(
        "Diretório Raiz dos Dados", value=default_path)

    include_subdirs = st.checkbox("Buscar em Subdiretórios", value=True)
    delimiter = st.text_input("Delimitador CSV", value=";")

    # Botão para iniciar a busca e análise
    if st.button("Carregar e Analisar Dados"):
        with st.spinner("Buscando e processando informações dos arquivos..."):
            if os.path.isdir(root_directory):
                # Guarda a lista de arquivos e anos no estado da sessão
                st.session_state.parsed_files = find_and_parse_files(
                    root_directory, include_subdirs)
                if not st.session_state.parsed_files:
                    st.warning(
                        "Nenhum arquivo CSV com formato AAAA-MM foi encontrado.")
                else:
                    st.session_state.data_loaded = True
                    st.success(
                        f"Encontrados {len(st.session_state.parsed_files)} arquivos relevantes.")
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

    analysis_mode = st.radio(
        "Escolha como deseja analisar os dados:",
        ("Por Arquivo", "Por Ano", "Conjunto Completo"),
        horizontal=True
    )

    files_to_process = []
    report_title = ""

    # --- Lógica de Seleção de Dados ---
    if analysis_mode == "Por Arquivo":
        st.subheader("Análise por Arquivo Individual")
        file_options = {os.path.relpath(
            path, root_directory): path for path, year in st.session_state.parsed_files}
        selected_display = st.selectbox(
            "Selecione um arquivo:", list(file_options.keys()))
        if selected_display:
            files_to_process = [file_options[selected_display]]
            report_title = f"Relatório de Análise para o Arquivo: {selected_display}"

    elif analysis_mode == "Por Ano":
        st.subheader("Análise Agregada por Ano")
        available_years = sorted(
            list(set(year for path, year in st.session_state.parsed_files)), reverse=True)
        selected_year = st.selectbox("Selecione um ano:", available_years)
        if selected_year:
            files_to_process = [
                path for path, year in st.session_state.parsed_files if year == selected_year]
            report_title = f"Relatório de Análise Agregado para o Ano: {selected_year}"
            st.write(
                f"Serão concatenados {len(files_to_process)} arquivos para o ano de {selected_year}.")

    elif analysis_mode == "Conjunto Completo":
        st.subheader("Análise do Conjunto de Dados Completo")
        files_to_process = [path for path,
                            year in st.session_state.parsed_files]
        report_title = "Relatório de Análise para o Conjunto de Dados Completo"
        st.write(
            f"Serão concatenados todos os {len(files_to_process)} arquivos encontrados.")

    # --- Geração e Exibição do Relatório ---
    if files_to_process:
        st.header("3. Relatório de Perfilamento")

        with st.spinner(f"Processando... Isto pode levar alguns minutos, especialmente para análises agregadas."):
            try:
                # Carrega e concatena os arquivos selecionados
                df_aggregated = load_and_concat_data(
                    files_to_process, delimiter.replace('\\t', '\t'))

                if df_aggregated is not None and not df_aggregated.empty:
                    # Gera o relatório
                    profile = generate_profile_report(
                        df_aggregated, title=report_title)

                    # Converte para HTML e exibe
                    report_html = profile.to_html()
                    st.components.v1.html(
                        report_html, height=800, scrolling=True)
                else:
                    st.error(
                        "Não foi possível carregar dados para a seleção atual.")

            except Exception as e:
                st.error(f"Ocorreu um erro ao gerar o relatório: {e}")

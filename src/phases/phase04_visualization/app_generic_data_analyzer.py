# -*- coding: utf-8 -*-

# --------------------------------------------------------------------------------
# Descrição: [Manter a descrição original, se houver. Se não, adicione uma descrição concisa do propósito do script em português.]
# Exemplo de uso: python app_generic_data_analyzer.py --argumento valor
#
# Autor: Marcelo Anaissi
# Criado em: 29/05/2025
# Versão: 1.0
#
# Modificado por: Jules
# Modificado em: 21/07/2025
# Licença: MIT
# --------------------------------------------------------------------------------
import pandas as pd
from ydata_profiling import ProfileReport
import streamlit as st
from src.utils import read_csv_robust

# --- Funções de Lógica de Dados ---

def load_data(file_path, delimiter=';'):
    """
    Carrega dados de um arquivo CSV ou Excel.
    """
    if not isinstance(file_path, str) or not file_path:
        raise ValueError("Caminho do arquivo inválido.")

    if file_path.endswith('.xlsx'):
        return pd.read_excel(file_path)
    elif file_path.endswith('.csv'):
        return read_csv_robust(file_path, delimiter=delimiter)
    else:
        raise ValueError("Formato de arquivo não suportado. Apenas os formatos XLSX e CSV são permitidos.")

def get_data_summary(data):
    """
    Retorna um resumo estatístico do DataFrame.
    """
    return data.describe(include='all')

# --- Funções de Interface do Usuário ---

def show_first_rows(data):
    st.subheader("Primeiras 5 linhas:")
    st.write(data.head())
    rows_total = "{:,}".format(data.shape[0])
    st.write(f"Linhas: {rows_total} | Colunas: {data.shape[1]}")

def show_data_types(data):
    st.subheader("Tipos de Dados:")
    st.write(data.dtypes)

def show_column_data_summary(data):
    st.subheader("Resumo dos Dados por Coluna:")
    st.info("top = valor mais frequente, freq = número de ocorrências do valor mais frequente", icon="ℹ️")
    st.write(get_data_summary(data))

def show_missing_values(data):
    st.subheader("Valores Ausentes:")
    st.write(data.isnull().sum())

def show_correlation_matrix(data):
    st.subheader("Matriz de Correlação:")
    st.write(data.corr())

def show_profile_report(data):
    profile = ProfileReport(data, title="Relatório de Perfil do Pandas")
    with st.expander("Perfil:"):
        st.write(profile)

def run_app():
    """
    Executa a aplicação Streamlit.
    """
    st.title("Análise de Dados com Streamlit")

    file_path = st.text_input("Digite o caminho para o seu arquivo (XLSX ou CSV):")
    if file_path:
        try:
            data = load_data(file_path)
            show_first_rows(data)
            show_data_types(data)
            show_column_data_summary(data)
            show_missing_values(data)
            # show_correlation_matrix(data) # Comentado por padrão
            show_profile_report(data)

        except FileNotFoundError:
            st.error("Arquivo não encontrado. Por favor, verifique o caminho do arquivo.")
        except Exception as e:
            st.error(f"Ocorreu um erro: {str(e)}")

if __name__ == "__main__":
    run_app()

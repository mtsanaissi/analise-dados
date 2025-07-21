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
from utils import read_csv_robust


def load_data(file_path):
    if file_path.endswith('.xlsx'):
        data = pd.read_excel(file_path)
    elif file_path.endswith('.csv'):
        data = read_csv_robust(file_path, delimiter=';')
    else:
        raise ValueError(
            "File format not supported. Only XLSX and CSV formats are allowed.")
    return data


def first_rows(data):
    # Show first 5 rows of the data
    st.subheader("First 5 rows:")
    st.write(data.head())
    rows_total = "{:,}".format(data.shape[0])
    st.write(f"Rows: {rows_total} | Columns: {data.shape[1]}")


def data_types(data):
    # Show data types of each column
    st.subheader("Data types:")
    st.write(data.dtypes)


def column_data_summary(data):
    # Summary statistics for each column
    st.subheader("Column-wise Data Summary:")
    st.info("top = most frequent value, freq = number of occurrences of most frequent value", icon="ℹ️")
    st.write(data.describe(include='all'))


def missing_values(data):
    # Check for missing values
    st.subheader("Missing Values:")
    st.write(data.isnull().sum())


def correlation_matrix(data):
    # Correlation matrix
    st.subheader("Correlation Matrix:")
    st.write(data.corr())


def show_profile(data):
    profile = ProfileReport(data, title="Pandas Profiling Report")
    with st.expander("Profile:"):
        profile


def main():
    st.title("Data Analysis with Streamlit")

    file_path = st.text_input("Enter the path to your file (XLSX or CSV):")
    if file_path:
        try:
            data = load_data(file_path)
            # Convert columns to datetime format
            # data['Date'] = pd.to_datetime(data['Date'], format='%d/%m/%Y')
            # Fix float values
            # data['ColumnName'] = data['ColumnName'].str.replace(',', '.').astype(float)
            first_rows(data)
            data_types(data)
            column_data_summary(data)
            missing_values(data)
            # correlation_matrix(data)

            show_profile(data)

        except FileNotFoundError:
            st.error("File not found. Please check the file path.")
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")


if __name__ == "__main__":
    main()

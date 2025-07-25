# -*- coding: utf-8 -*-

import os
import pandas as pd
import json
import numpy as np
from src.utils import find_files  # Importa a função centralizada


# Lista de formatos de data comuns para teste rápido
COMMON_DATE_FORMATS = [
    # Formatos mais comuns primeiro
    '%Y-%m-%d %H:%M:%S', '%d/%m/%Y %H:%M', '%Y-%m-%d', '%d/%m/%Y',
    # Formatos americanos
    '%m/%d/%Y %H:%M:%S', '%m/%d/%Y',
    # Formatos com nomes de mês, etc.
    '%d %b %Y', '%Y-%m-%d %H:%M:%S.%f',
]


def profile_dataframe(df):
    """
    Realiza o perfilamento de um DataFrame, analisando cada coluna.
    Retorna uma lista de dicionários, onde cada dicionário representa o perfil de uma coluna.
    """
    profile_results = []

    for col_name in df.columns:
        column_series = df[col_name]

        col_profile = {
            "nome_coluna": col_name,
            "tipo_pandas": str(column_series.dtype),
            "tipo_inferido": "Indeterminado",
            "estatisticas": {
                "total_registros": len(column_series),
                "valores_nao_nulos": int(column_series.count()),
                "valores_ausentes": int(column_series.isnull().sum()),
                "percentual_ausentes": round(column_series.isnull().mean() * 100, 2),
                "valores_unicos": int(column_series.nunique())
            }
        }

        if col_profile["estatisticas"]["valores_nao_nulos"] == 0:
            col_profile["tipo_inferido"] = "Vazio"
            profile_results.append(col_profile)
            continue

        numeric_series = pd.to_numeric(column_series.dropna(), errors='coerce')
        if (numeric_series.count() / column_series.count()) > 0.8:
            col_profile["tipo_inferido"] = "Numérico"
            col_profile["estatisticas"].update({
                "min": float(numeric_series.min()), "max": float(numeric_series.max()),
                "media": float(numeric_series.mean()), "mediana": float(numeric_series.median()),
                "desvio_padrao": float(numeric_series.std()), "soma": float(numeric_series.sum()),
                # Corrigido para 0.75
                "quantil_25": float(numeric_series.quantile(0.25)), "quantil_75": float(numeric_series.quantile(0.75)),
                "contagem_zeros": int((numeric_series == 0).sum())
            })

        elif col_profile["tipo_inferido"] == "Indeterminado":
            datetime_series = None
            detected_format = None

            for date_format in COMMON_DATE_FORMATS:
                try:
                    temp_series = pd.to_datetime(
                        column_series.dropna(), format=date_format, errors='coerce')
                    if (temp_series.count() / column_series.count()) > 0.8:
                        datetime_series = temp_series
                        detected_format = date_format
                        break
                except (ValueError, TypeError):
                    continue

            if datetime_series is not None:
                col_profile["tipo_inferido"] = "Data/Hora"
                col_profile["estatisticas"]["formato_data_detectado"] = detected_format
                earliest_date, latest_date = datetime_series.min(), datetime_series.max()
                col_profile["estatisticas"].update({
                    "data_minima": earliest_date.isoformat() if pd.notna(earliest_date) else None,
                    "data_maxima": latest_date.isoformat() if pd.notna(latest_date) else None,
                })

        if col_profile["tipo_inferido"] == "Indeterminado":
            if column_series.nunique() == 2:
                col_profile["tipo_inferido"] = "Booleano/Binário"
                value_counts = column_series.value_counts().to_dict()
                col_profile["estatisticas"]["distribuicao"] = {
                    str(k): int(v) for k, v in value_counts.items()}
            else:
                col_profile["tipo_inferido"] = "Categórico/Texto"

        if col_profile["tipo_inferido"] in ["Categórico/Texto", "Booleano/Binário"] or \
           (col_profile["tipo_inferido"] == "Numérico" and column_series.nunique() < 25):

            if "distribuicao" not in col_profile["estatisticas"]:
                top_5_counts = column_series.value_counts().nlargest(5).to_dict()
                col_profile["estatisticas"]["valores_mais_frequentes"] = {
                    str(k): int(v) for k, v in top_5_counts.items()}

        profile_results.append(col_profile)

    return profile_results


def analyze_data_profiling(root_directory, extensions=['csv', 'xlsx', 'json', 'xls'], recursive=True, delimiter=","):
    """
    Orquestra o perfilamento de dados para múltiplos arquivos em um diretório.
    Retorna uma lista de dicionários, onde cada dicionário contém o perfil de um arquivo.
    """
    if not os.path.isdir(root_directory):
        return {"status": "error", "message": f"O diretório '{root_directory}' não existe ou não é um diretório.", "profiles": []}

    discovered_files = find_files(root_directory, extensions, recursive)
    if not discovered_files:
        return {"status": "success", "message": "Nenhum arquivo encontrado com os critérios especificados.", "profiles": []}

    full_report = []

    for file_path in discovered_files:
        relative_path = os.path.relpath(file_path, root_directory)
        _, file_ext_with_dot = os.path.splitext(file_path)
        extension = file_ext_with_dot.lstrip('.').lower()

        try:
            df = None
            if extension == 'csv':
                df = pd.read_csv(file_path, sep=delimiter, low_memory=False)
            elif extension in ['xlsx', 'xls']:
                xls = pd.ExcelFile(file_path)
                # Para Excel, perfilamos cada planilha separadamente
                for sheet_name in xls.sheet_names:
                    df_sheet = pd.read_excel(xls, sheet_name=sheet_name)
                    profile = profile_dataframe(df_sheet)
                    full_report.append({
                        "arquivo": relative_path,
                        "planilha": sheet_name,
                        "perfil_colunas": profile
                    })
                continue  # Pula para o próximo arquivo, pois as planilhas já foram processadas

            elif extension == 'json':
                try:
                    df = pd.read_json(file_path, lines=True)
                except (ValueError, TypeError):
                    df = pd.read_json(file_path)

            if df is not None:
                profile = profile_dataframe(df)
                full_report.append(
                    {"arquivo": relative_path, "perfil_colunas": profile})

        except Exception as e:
            full_report.append({"arquivo": relative_path, "erro": str(e)})

    return {"status": "success", "message": "Perfilamento de dados concluído.", "profiles": full_report}

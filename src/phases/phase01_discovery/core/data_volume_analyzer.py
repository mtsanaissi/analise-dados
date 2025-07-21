# -*- coding: utf-8 -*-

import os
import pandas as pd
import json
import sys

def get_file_metrics(file_path, delimiter):
    """
    Obtém métricas (registros e tamanho) para um único arquivo, despachando para a função correta.
    """
    _, file_ext_with_dot = os.path.splitext(file_path)
    extension = file_ext_with_dot.lstrip('.').lower()

    file_size = os.path.getsize(file_path)
    record_count = 0
    error_message = None

    try:
        if extension == 'csv':
            df = pd.read_csv(file_path, sep=delimiter)
            record_count = len(df)
        elif extension in ['xlsx', 'xls']:
            xls = pd.ExcelFile(file_path)
            for sheet_name in xls.sheet_names:
                df = pd.read_excel(xls, sheet_name=sheet_name)
                record_count += len(df)
        elif extension == 'json':
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        record_count = len(data)
                    elif isinstance(data, dict):
                        record_count = 1
            except (json.JSONDecodeError, TypeError):
                try:
                    df = pd.read_json(file_path, lines=True)
                    record_count = len(df)
                except (ValueError, TypeError):
                    raise ValueError(
                        "Formato JSON não suportado (nem padrão, nem Lines).")

    except pd.errors.EmptyDataError:
        record_count = 0
    except Exception as e:
        error_message = str(e)
        record_count = 0

    return {
        "arquivo": file_path,
        "extensao": extension,
        "registros": record_count,
        "tamanho_bytes": file_size,
        "erro": error_message
    }


def format_bytes(size_bytes):
    """
    Formata um tamanho em bytes para uma unidade mais legível (KB, MB, GB).
    """
    if size_bytes is None:
        return "N/A"
    if size_bytes < 1024:
        return f"{size_bytes} B"
    if size_bytes < 1024**2:
        return f"{size_bytes/1024:.2f} KB"
    if size_bytes < 1024**3:
        return f"{size_bytes/1024**2:.2f} MB"
    return f"{size_bytes/1024**3:.2f} GB"


def analyze_data_volume(discovered_files, delimiter=";"):
    """
    Analisa o volume de dados (contagem de registros e tamanho) para uma lista de arquivos.
    Retorna um dicionário com o resumo agregado e detalhes dos arquivos com erro.
    """
    all_metrics = [get_file_metrics(f, delimiter) for f in discovered_files]

    files_with_errors = [m for m in all_metrics if m['erro']]
    valid_metrics = [m for m in all_metrics if not m['erro']]

    if not valid_metrics:
        return {
            "summary": [],
            "files_with_errors": files_with_errors,
            "message": "Nenhum arquivo pôde ser lido com sucesso para gerar o resumo."
        }

    df_metrics = pd.DataFrame(valid_metrics)

    summary_df = df_metrics.groupby('extensao').agg(
        total_arquivos=('arquivo', 'count'),
        total_registros=('registros', 'sum'),
        total_tamanho_bytes=('tamanho_bytes', 'sum')
    ).reset_index()

    summary_df['media_registros_por_arquivo'] = summary_df['total_registros'] / summary_df['total_arquivos']
    summary_df['media_tamanho_por_arquivo'] = summary_df['total_tamanho_bytes'] / summary_df['total_arquivos']

    # Converte o DataFrame de resumo para uma lista de dicionários para retorno
    summary_list = summary_df.to_dict(orient='records')

    # Calcula o total geral
    total_arquivos_geral = summary_df['total_arquivos'].sum()
    total_registros_geral = summary_df['total_registros'].sum()
    total_tamanho_geral = summary_df['total_tamanho_bytes'].sum()

    overall_summary = {
        "total_arquivos_geral": total_arquivos_geral,
        "total_registros_geral": total_registros_geral,
        "total_tamanho_geral_bytes": total_tamanho_geral,
        "total_tamanho_geral_formatado": format_bytes(total_tamanho_geral)
    }

    return {
        "summary_by_extension": summary_list,
        "overall_summary": overall_summary,
        "files_with_errors": files_with_errors,
        "message": "Resumo de volume e tamanho gerado com sucesso."
    }


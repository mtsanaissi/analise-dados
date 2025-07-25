# -*- coding: utf-8 -*-

import os
import pandas as pd
from src.utils import find_files
from src.connectors.factory import get_data_loader


def get_csv_header(filepath, delimiter=None):
    """
    Lê o cabeçalho de um arquivo CSV usando o conector de dados.
    Retorna a lista de colunas do cabeçalho ou um dicionário de erro.
    """
    try:
        data_loader = get_data_loader(filepath, delimiter=delimiter)
        df = data_loader.read()

        if df is None:
            return {"error": "Falha na leitura do arquivo (ver logs de erro)."}

        if df.empty:
            if len(df.columns) == 0:
                return {"header": [], "message": "Arquivo CSV vazio ou sem cabeçalho."}
            else:
                return {"header": [str(col).strip() for col in df.columns], "message": "Arquivo CSV com cabeçalho mas sem dados."}

        return {"header": [str(col).strip() for col in df.columns]}

    except FileNotFoundError:
        return {"error": "Arquivo não encontrado."}
    except ValueError as e:
        return {"error": f"Erro no conector: {e}"}
    except Exception as e:
        return {"error": f"Erro geral ao ler o cabeçalho: {e}"}


def get_csv_headers(filepath, delimiter=None):
    """
    Lê o cabeçalho de um arquivo CSV e retorna apenas a lista de colunas.

    Args:
        filepath (str): O caminho para o arquivo CSV.
        delimiter (str, optional): O delimitador a ser usado. Defaults to None.
    """
    result = get_csv_header(filepath, delimiter=delimiter)
    return result.get("header", [])


def check_csv_structures(root_directory, detected_delimiters_map=None):
    """
    Verifica se todos os arquivos CSV em um diretório (e subdiretórios)
    possuem a mesma estrutura de cabeçalho.
    Retorna uma lista de dicionários com o resultado da verificação para cada arquivo.
    """
    if detected_delimiters_map is None:
        detected_delimiters_map = {}

    if not os.path.isdir(root_directory):
        return {"status": "error", "message": f"O diretório '{root_directory}' não existe ou não é um diretório.", "results": []}

    csv_files = find_files(root_directory, ['csv'], recursive=True)
    csv_files.sort()

    if not csv_files:
        return {"status": "success", "message": f"Nenhum arquivo .csv encontrado em '{root_directory}'.", "results": []}

    reference_header = None
    reference_filepath = None
    all_file_reports = []

    for filepath in csv_files:
        relative_path = os.path.relpath(filepath, root_directory)
        file_report = {"file": os.path.basename(
            filepath), "status": "Pendente", "details": {}}

        delimiter = detected_delimiters_map.get(filepath)

        print(f"Processando arquivo: {filepath}")  # DEBUG
        header_result = get_csv_header(filepath, delimiter=delimiter)
        print(f"Resultado do cabeçalho: {header_result}")  # DEBUG

        if "error" in header_result:
            file_report["status"] = "Erro"
            file_report["details"]["error_message"] = header_result['error']
            all_file_reports.append(file_report)
            print(f"Relatório do arquivo (Erro): {file_report}")  # DEBUG
            continue

        current_header = header_result.get("header")

        if current_header is None or len(current_header) == 0:
            file_report["status"] = "Atenção"
            file_report["details"]["message"] = header_result.get(
                "message", "CSV vazio ou sem cabeçalho.")
            all_file_reports.append(file_report)
            # DEBUG
            print(
                f"Relatório do arquivo (Atenção - sem cabeçalho): {file_report}")
            continue

        if reference_header is None:
            reference_header = current_header
            reference_filepath = relative_path
            file_report["status"] = "Referência"
            file_report["details"]["message"] = "Definido como arquivo de referência."
        else:
            if len(current_header) != len(reference_header):
                file_report["status"] = "Inconsistente"
                file_report["details"]["message"] = (f"Número de colunas diferente. Esperado: {len(reference_header)}, "
                                                     f"Encontrado: {len(current_header)}.")
            elif current_header != reference_header:
                file_report["status"] = "Inconsistente"
                diff_reason = "Nomes/ordem das colunas diferente."
                for i, (ref_col, cur_col) in enumerate(zip(reference_header, current_header)):
                    if ref_col != cur_col:
                        diff_reason = (f"Diferença na coluna {i+1}. "
                                       f"Esperado: '{ref_col}', Encontrado: '{cur_col}'.")
                        break
                file_report["details"]["message"] = diff_reason
            else:
                file_report["status"] = "OK"
                file_report["details"]["message"] = "Estrutura consistente com o arquivo de referência."

        all_file_reports.append(file_report)
        print(f"Relatório do arquivo (Final): {file_report}")  # DEBUG

    return {"status": "success", "message": "Verificação de estrutura CSV concluída.", "results": all_file_reports}

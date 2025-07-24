# -*- coding: utf-8 -*-

import os
import pandas as pd
from utils import find_files # Importa a função centralizada
from connectors.factory import get_data_loader # Importa a fábrica de conectores


def get_csv_header(filepath):
    """
    Lê o cabeçalho de um arquivo CSV usando o conector de dados.
    Retorna a lista de colunas do cabeçalho ou um dicionário de erro.
    """
    try:
        data_loader = get_data_loader(filepath)
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


def get_csv_headers(filepath):
    """
    Lê o cabeçalho de um arquivo CSV e retorna apenas a lista de colunas.
    """
    result = get_csv_header(filepath)
    return result.get("header", [])


def check_csv_structures(root_directory):
    """
    Verifica se todos os arquivos CSV em um diretório (e subdiretórios)
    possuem a mesma estrutura de cabeçalho.
    Retorna um dicionário com o resultado da verificação.
    """
    if not os.path.isdir(root_directory):
        return {"status": "error", "message": f"O diretório '{root_directory}' não existe ou não é um diretório.", "results": {}}

    csv_files = find_files(root_directory, ['csv'], recursive=True)
    csv_files.sort()

    if not csv_files:
        return {"status": "success", "message": f"Nenhum arquivo .csv encontrado em '{root_directory}'.", "results": {}}

    reference_header = None
    reference_filepath = None
    inconsistent_files = {}
    consistent_files_count = 0
    total_files_processed = 0

    for filepath in csv_files:
        total_files_processed += 1
        relative_path = os.path.relpath(filepath, root_directory)
        
        header_result = get_csv_header(filepath)

        if "error" in header_result:
            inconsistent_files[str(relative_path)] = f"Erro ao obter cabeçalho: {header_result['error']}"
            continue
        
        current_header = header_result.get("header")
        
        if current_header is None or len(current_header) == 0:
            inconsistent_files[str(relative_path)] = header_result.get("message", "CSV vazio ou sem cabeçalho.")
            continue

        if reference_header is None:
            reference_header = current_header
            reference_filepath = relative_path
            consistent_files_count += 1
        else:
            if len(current_header) != len(reference_header):
                msg = (f"Número de colunas diferente. Esperado: {len(reference_header)}, "
                       f"Encontrado: {len(current_header)}.")
                inconsistent_files[str(relative_path)] = msg
            elif current_header != reference_header:
                diff_reason = "Nomes/ordem das colunas diferente."
                for i, (ref_col, cur_col) in enumerate(zip(reference_header, current_header)):
                    if ref_col != cur_col:
                        diff_reason = (f"Diferença na coluna {i+1}. "
                                       f"Esperado: '{ref_col}', Encontrado: '{cur_col}'.")
                        break
                inconsistent_files[str(relative_path)] = diff_reason
            else:
                consistent_files_count += 1
    
    status = "success" if not inconsistent_files else "warning"
    message = "Todos os arquivos CSV analisados possuem a mesma estrutura." if not inconsistent_files else "Alguns arquivos CSV possuem estrutura inconsistente ou erros."

    return {
        "status": status,
        "message": message,
        "total_files_processed": total_files_processed,
        "consistent_files_count": consistent_files_count,
        "reference_header": reference_header,
        "reference_filepath": reference_filepath,
        "inconsistent_files": inconsistent_files
    }


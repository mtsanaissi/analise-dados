import pandas as pd
import gc
import logging


def get_excel_columns(excel_file):
    """
    Obtém as colunas de um arquivo Excel usando um objeto ExcelFile já aberto.

    Args:
        excel_file (pd.ExcelFile): Objeto ExcelFile já aberto

    Returns:
        list: Lista de nomes das colunas
    """
    try:
        # Lê apenas o cabeçalho (nrows=0) da primeira planilha
        sheet_name = excel_file.sheet_names[0]
        df = pd.read_excel(excel_file, sheet_name=sheet_name, nrows=0)
        columns = list(df.columns)

        # Limpeza explícita
        del df
        gc.collect()

        return columns
    except Exception as e:
        logging.error(f"Erro ao obter colunas: {e}")
        return []


def analyze_excel_sheets(excel_file):
    """
    Analisa as planilhas de um arquivo Excel usando um objeto ExcelFile já aberto.

    Args:
        excel_file (pd.ExcelFile): Objeto ExcelFile já aberto

    Returns:
        dict: Resultado da análise das planilhas
    """
    analysis_result = {
        "sheet_count": 0,
        "sheet_names": [],
        "sheets_info": {}
    }

    try:
        sheet_names = excel_file.sheet_names
        analysis_result["sheet_count"] = len(sheet_names)
        analysis_result["sheet_names"] = sheet_names

        for sheet_name in sheet_names:
            try:
                # Lê apenas algumas linhas para análise rápida
                df = pd.read_excel(excel_file, sheet_name=sheet_name, nrows=5)

                sheet_info = {
                    "columns": list(df.columns),
                    "column_count": len(df.columns),
                    "sample_row_count": len(df),
                }

                analysis_result["sheets_info"][sheet_name] = sheet_info

                # Limpeza explícita após cada planilha
                del df
                gc.collect()

            except Exception as e:
                logging.error(f"Erro ao analisar planilha '{sheet_name}': {e}")
                analysis_result["sheets_info"][sheet_name] = {
                    "error": str(e)
                }

        return analysis_result

    except Exception as e:
        logging.error(f"Erro na análise geral das planilhas: {e}")
        return {
            "error": str(e),
            "sheet_count": 0,
            "sheet_names": [],
            "sheets_info": {}
        }
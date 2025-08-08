import pandas as pd
import logging
from typing import Dict, Any, List, Union
import numpy as np
import re

def _apply_corrections(df: pd.DataFrame, corrections: Union[Dict, List[Dict]]) -> pd.DataFrame:
    """
    Aplica correções a um DataFrame com base em um mapa ou uma lista de regras.
    """
    df_corrected = df.copy()

    if isinstance(corrections, dict):
        df_corrected.replace(corrections, inplace=True)
        return df_corrected

    if isinstance(corrections, list):
        for rule in corrections:
            if not isinstance(rule, dict):
                continue

            column = rule.get('column')
            existing_value = rule.get('existing_value')
            new_value = rule.get('new_value')
            case_sensitive = rule.get('case_sensitive', True)

            if column:
                if column in df_corrected.columns:
                    if not case_sensitive and pd.api.types.is_string_dtype(df_corrected[column]):
                        if isinstance(existing_value, str):
                            df_corrected[column] = df_corrected[column].str.replace(f'^{re.escape(existing_value)}$', str(new_value), case=False, regex=True)
                        elif isinstance(existing_value, list):
                            for val in existing_value:
                                df_corrected[column] = df_corrected[column].str.replace(f'^{re.escape(val)}$', str(new_value), case=False, regex=True)
                    else:
                        df_corrected[column] = df_corrected[column].replace(existing_value, new_value)
            else:
                for col_name in df_corrected.columns:
                    # This is a global rule, apply it to all columns
                    if not case_sensitive and pd.api.types.is_string_dtype(df_corrected[col_name]):
                        if isinstance(existing_value, str):
                           df_corrected[col_name] = df_corrected[col_name].mask(df_corrected[col_name].str.lower() == existing_value.lower(), new_value)
                        elif isinstance(existing_value, list):
                            for val in existing_value:
                                df_corrected[col_name] = df_corrected[col_name].mask(df_corrected[col_name].str.lower() == val.lower(), new_value)
                    else:
                        if isinstance(existing_value, list):
                            for val in existing_value:
                                df_corrected[col_name] = df_corrected[col_name].replace(val, new_value)
                        else:
                            df_corrected[col_name] = df_corrected[col_name].replace(existing_value, new_value)


    return df_corrected

def correct_values(input_file: str, output_file: str, corrections: Union[Dict, List[Dict]]) -> Dict[str, Any]:
    """
    Lê um arquivo, aplica correções de valor e salva o resultado.

    Args:
        input_file (str): O caminho para o arquivo de entrada.
        output_file (str): O caminho para o arquivo de saída.
        corrections (Union[Dict, List[Dict]]): Um dicionário para substituições globais
                                               ou uma lista de dicionários com regras de correção.

    Returns:
        Dict[str, Any]: Um dicionário com o status da operação.
    """
    logger = logging.getLogger(__name__)
    try:
        try:
            df = pd.read_csv(input_file, sep=';')
        except (pd.errors.ParserError, ValueError):
            df = pd.read_csv(input_file)

        df_corrected = _apply_corrections(df, corrections)

        df_corrected.to_csv(output_file, index=False, sep=';')
        return {
            "status": "success",
            "message": f"Correção de valores concluída. {len(df_corrected)} linhas no arquivo de saída.",
            "report_path": output_file
        }
    except Exception as e:
        logger.error(f"Erro durante a correção de valores: {e}")
        return {
            "status": "error",
            "message": str(e),
            "report_path": None
        }

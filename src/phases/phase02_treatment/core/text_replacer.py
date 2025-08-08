# -*- coding: utf-8 -*-

# --------------------------------------------------------------------------------
# Descrição: Este módulo contém a lógica para substituição de texto em arquivos.
# Autor: Jules
# Criado em: 07/08/2025
# Versão: 1.0
# --------------------------------------------------------------------------------

import pandas as pd
import logging
from typing import Dict, Any
import re

def replace_text(input_file: str, output_file: str, replacements: list) -> Dict[str, Any]:
    """
    Lê um arquivo, aplica substituições de texto e salva o resultado.

    Args:
        input_file (str): O caminho para o arquivo de entrada.
        output_file (str): O caminho para o arquivo de saída.
        replacements (list): Uma lista de dicionários com as substituições a serem aplicadas.

    Returns:
        Dict[str, Any]: Um dicionário com o status da operação.
    """
    logger = logging.getLogger(__name__)
    try:
        df = pd.read_csv(input_file, sep=';', encoding='utf-8-sig')

        for rule in replacements:
            pattern = rule.get('pattern')
            new_value = rule.get('new_value')
            column = rule.get('column')
            is_regex = rule.get('is_regex', False)
            case_sensitive = rule.get('case_sensitive', True)

            if not all([pattern, new_value, column]):
                logger.warning(f"Regra de substituição de texto incompleta: {rule}. Pulando.")
                continue

            if column in df.columns:
                if pd.api.types.is_object_dtype(df[column]):
                    if is_regex:
                        flags = re.IGNORECASE if not case_sensitive else 0
                        df[column] = df[column].str.replace(pattern, new_value, regex=True, flags=flags)
                    else:
                        df[column] = df[column].str.replace(pattern, new_value, regex=False)
                else:
                    logger.warning(f"  -> A coluna '{column}' não é do tipo texto/objeto no arquivo {input_file}. A regra será ignorada.")
                    continue
            else:
                logger.warning(f"  -> A coluna '{column}' especificada na regra não existe no arquivo {input_file}. A regra será ignorada.")
                continue

        df.to_csv(output_file, index=False, sep=';', encoding='utf-8-sig')

        return {
            "status": "success",
            "message": f"Substituição de texto concluída. {len(df)} linhas no arquivo de saída.",
            "report_path": output_file
        }
    except Exception as e:
        logger.error(f"Erro durante a substituição de texto: {e}")
        return {
            "status": "error",
            "message": str(e),
            "report_path": None
        }

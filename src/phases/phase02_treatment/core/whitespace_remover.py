# -*- coding: utf-8 -*-

# --------------------------------------------------------------------------------
# Descrição: Este módulo contém a lógica para remoção de espaços em branco.
# Autor: Jules
# Criado em: 07/08/2025
# Versão: 1.0
# --------------------------------------------------------------------------------

import pandas as pd
import logging
from typing import Dict, Any

def remove_whitespace(input_file: str, output_file: str) -> Dict[str, Any]:
    """
    Lê um arquivo, remove espaços em branco e salva o resultado.

    Args:
        input_file (str): O caminho para o arquivo de entrada.
        output_file (str): O caminho para o arquivo de saída.

    Returns:
        Dict[str, Any]: Um dicionário com o status da operação.
    """
    logger = logging.getLogger(__name__)
    try:
        df = pd.read_csv(input_file, sep=';', encoding='utf-8-sig', quotechar='"', skipinitialspace=True)

        df.columns = df.columns.str.strip()

        for col in df.columns:
            if df[col].dtype == 'object':
                df[col] = df[col].str.strip()

        df.to_csv(output_file, index=False, sep=';', encoding='utf-8-sig')

        return {
            "status": "success",
            "message": f"Remoção de espaços em branco concluída. {len(df)} linhas no arquivo de saída.",
            "report_path": output_file
        }
    except Exception as e:
        logger.error(f"Erro durante a remoção de espaços em branco: {e}")
        return {
            "status": "error",
            "message": str(e),
            "report_path": None
        }

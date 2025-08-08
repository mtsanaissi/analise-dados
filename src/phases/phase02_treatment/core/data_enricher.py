# -*- coding: utf-8 -*-

# --------------------------------------------------------------------------------
# Descrição: Este script define a classe DataEnricher, responsável por
#            enriquecer um conjunto de dados principal com informações de uma
#            fonte de dados secundária (consulta).
# Exemplo de uso: Esta classe é projetada para ser usada dentro do orquestrador
#                 da Fase 2, e não diretamente pela linha de comando.
#
# Autor: Jules
# Criado em: 25/07/2025
# Versão: 1.0
#
# Modificado por: Gemini
# Modificado em: 25/07/2025
# Licença: MIT
# --------------------------------------------------------------------------------

import pandas as pd
import logging
import os
from typing import Dict, Any

def enrich_data(main_file: str, lookup_file: str, main_key: str, lookup_key: str, columns_to_add: list, output_file: str, join_how: str = 'left', sep: str = ',') -> Dict[str, Any]:
    """
    Enriquece um dataframe principal com dados de um dataframe de consulta.

    Args:
        main_file (str): Caminho para o arquivo principal.
        lookup_file (str): Caminho para o arquivo de consulta.
        main_key (str): Chave de junção no arquivo principal.
        lookup_key (str): Chave de junção no arquivo de consulta.
        columns_to_add (list): Colunas a serem adicionadas do arquivo de consulta.
        output_file (str): Caminho para salvar o arquivo enriquecido.
        join_how (str): Tipo de junção a ser realizada. Padrão 'left'.
        sep (str): Delimitador dos arquivos CSV.

    Returns:
        Dict[str, Any]: Um dicionário com o status da operação.
    """
    logger = logging.getLogger(__name__)
    try:
        if not all([main_file, lookup_file, main_key, lookup_key, columns_to_add, output_file]):
            raise ValueError("Todos os parâmetros para enrich_data devem ser fornecidos.")

        logger.info(f"Carregando arquivo principal de: {main_file}")
        df_main = pd.read_csv(main_file, sep=sep)

        logger.info(f"Carregando arquivo de consulta de: {lookup_file}")
        df_lookup = pd.read_csv(lookup_file, sep=sep)

        # Validação da existência das colunas de junção
        if main_key not in df_main.columns:
            raise ValueError(
                f"A coluna de junção '{main_key}' não foi encontrada no arquivo principal: {main_file}")
        if lookup_key not in df_lookup.columns:
            raise ValueError(
                f"A coluna de junção '{lookup_key}' não foi encontrada no arquivo de consulta: {lookup_file}")

        logger.info(
            f"Verificando duplicatas na coluna de junção '{lookup_key}' do arquivo de consulta.")

        if df_lookup[lookup_key].duplicated().any():
            duplicated_keys = df_lookup[df_lookup[lookup_key].duplicated()][lookup_key]
            count = duplicated_keys.nunique()
            warning_message = f"Valores duplicados encontrados na coluna de junção '{lookup_key}': {count}."
            logger.warning(warning_message)

            keys_to_nullify = duplicated_keys.unique()
            for col in columns_to_add:
                if col not in df_main.columns:
                    df_main[col] = pd.NA
                df_main.loc[df_main[main_key].isin(keys_to_nullify), col] = pd.NA

            df_lookup_deduplicated = df_lookup.drop_duplicates(
                subset=[lookup_key], keep='first')
        else:
            df_lookup_deduplicated = df_lookup
            logger.info(
                "Nenhuma duplicata encontrada. Executando a junção.")

        df_enriched = pd.merge(
            df_main,
            df_lookup_deduplicated[columns_to_add + [lookup_key]],
            left_on=main_key,
            right_on=lookup_key,
            how=join_how,
            suffixes=('', '_lookup')
        )

        if main_key != lookup_key:
            df_enriched = df_enriched.drop(columns=[lookup_key])

        logger.info(f"Salvando o dataframe enriquecido em: {output_file}")
        df_enriched.to_csv(output_file, index=False)

        return {
            "status": "success",
            "message": f"Enriquecimento de dados concluído. {len(df_enriched)} linhas no arquivo de saída.",
            "report_path": output_file
        }
    except Exception as e:
        logger.error(f"Erro durante o enriquecimento de dados: {e}")
        return {
            "status": "error",
            "message": str(e),
            "report_path": None
        }

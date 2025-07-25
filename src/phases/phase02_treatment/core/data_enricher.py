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
# Modificado por:
# Modificado em:
# Licença: MIT
# --------------------------------------------------------------------------------

import pandas as pd
import logging
from typing import Dict, Any

class DataEnricher:
    """
    Uma classe para enriquecer um dataframe principal com dados de um dataframe de consulta.
    """

    def __init__(self, config: Dict[str, Any]):
        """
        Inicializa o DataEnricher com a configuração fornecida.

        Args:
            config (Dict[str, Any]): Um dicionário contendo os parâmetros de configuração.
                Esperado para conter 'main_file_path', 'query_file_path', 'join_on',
                'output_file_path', e opcionalmente 'join_how'.
        """
        self.config = config
        self.logger = logging.getLogger(__name__)

    def enrich_data(self) -> Dict[str, Any]:
        """
        Executa o processo de enriquecimento de dados.

        Carrega o arquivo de dados principal e o arquivo de consulta, verifica se há duplicatas
        na coluna de junção da consulta, executa a junção e salva o resultado.

        Returns:
            Dict[str, Any]: Um dicionário de status resumindo o resultado da operação.

        Raises:
            ValueError: Se chaves duplicadas forem encontradas na coluna de junção do arquivo de consulta.
        """
        main_file_path = self.config['main_file_path']
        query_file_path = self.config['query_file_path']
        join_on = self.config['join_on']
        output_file_path = self.config['output_file_path']
        join_how = self.config.get('join_how', 'left')

        self.logger.info(f"Carregando arquivo principal de: {main_file_path}")
        df_main = pd.read_csv(main_file_path)

        self.logger.info(f"Carregando arquivo de consulta de: {query_file_path}")
        df_query = pd.read_csv(query_file_path)

        self.logger.info(f"Verificando duplicatas na coluna de junção '{join_on}' do arquivo de consulta.")
        duplicated_keys = df_query[df_query.duplicated(subset=[join_on], keep=False)]

        if not duplicated_keys.empty:
            duplicated_values = duplicated_keys[join_on].unique()
            error_message = f"Chaves duplicadas encontradas no arquivo de consulta: {list(duplicated_values)}"
            self.logger.error(error_message)
            raise ValueError(error_message)

        self.logger.info("Nenhuma duplicata encontrada. Executando a junção.")
        df_enriched = pd.merge(df_main, df_query, on=join_on, how=join_how)

        self.logger.info(f"Salvando o dataframe enriquecido em: {output_file_path}")
        df_enriched.to_csv(output_file_path, index=False)

        status = {
            "main_file_rows": len(df_main),
            "query_file_rows": len(df_query),
            "enriched_file_rows": len(df_enriched),
            "output_file_path": output_file_path
        }
        self.logger.info(f"Processo de enriquecimento concluído. Status: {status}")

        return status

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
from typing import Dict, Any

class DataEnricher:
    """
    Uma classe para enriquecer um dataframe principal com dados de um dataframe de consulta.
    """

    def __init__(self, config: Dict[str, Any]):
        """
        Inicializa o DataEnricher com a configuração fornecida e valida as chaves necessárias.

        Args:
            config (Dict[str, Any]): Um dicionário contendo os parâmetros de configuração.
                As chaves esperadas são: 'main_file', 'lookup_file', 'main_key',
                'lookup_key', 'columns_to_add', 'output_file'.

        Raises:
            ValueError: Se alguma das chaves de configuração necessárias estiver faltando.
        """
        required_keys = ['main_file', 'lookup_file', 'main_key', 'lookup_key', 'columns_to_add', 'output_file']
        if not all(key in config for key in required_keys):
            missing_keys = set(required_keys) - set(config.keys())
            raise ValueError(f"Configuração de enriquecimento incompleta. Faltando chaves: {missing_keys}")

        self.config = config
        self.logger = logging.getLogger(__name__)

    def enrich_data(self) -> Dict[str, Any]:
        """
        Executa o processo de enriquecimento de dados.

        Carrega os arquivos, valida as colunas, verifica duplicatas na fonte de consulta,
        executa a junção e salva o resultado.

        Returns:
            Dict[str, Any]: Um dicionário de status resumindo o resultado da operação.

        Raises:
            ValueError: Se chaves de configuração estiverem faltando, colunas de junção
                        não forem encontradas ou se chaves duplicadas existirem no
                        arquivo de consulta.
        """
        main_file = self.config['main_file']
        lookup_file = self.config['lookup_file']
        main_key = self.config['main_key']
        lookup_key = self.config['lookup_key']
        columns_to_add = self.config['columns_to_add']
        output_file = self.config['output_file']
        join_how = self.config.get('join_how', 'left')

        self.logger.info(f"Carregando arquivo principal de: {main_file}")
        df_main = pd.read_csv(main_file)

        self.logger.info(f"Carregando arquivo de consulta de: {lookup_file}")
        df_lookup = pd.read_csv(lookup_file)

        # Validação da existência das colunas de junção
        if main_key not in df_main.columns:
            raise ValueError(f"A coluna de junção '{main_key}' não foi encontrada no arquivo principal: {main_file}")
        if lookup_key not in df_lookup.columns:
            raise ValueError(f"A coluna de junção '{lookup_key}' não foi encontrada no arquivo de consulta: {lookup_file}")

        self.logger.info(f"Verificando duplicatas na coluna de junção '{lookup_key}' do arquivo de consulta.")
        if df_lookup[lookup_key].duplicated().any():
            duplicated_values = df_lookup[df_lookup[lookup_key].duplicated()][lookup_key].unique()
            error_message = f"Chaves duplicadas encontradas no arquivo de consulta ('{lookup_key}'): {list(duplicated_values)}"
            self.logger.error(error_message)
            raise ValueError(error_message)

        self.logger.info("Nenhuma duplicata encontrada. Executando a junção.")
        df_enriched = pd.merge(
            df_main,
            df_lookup[columns_to_add + [lookup_key]], # Seleciona apenas as colunas necessárias do lookup
            left_on=main_key,
            right_on=lookup_key,
            how=join_how
        )

        # Garante que a coluna de junção do lookup não seja adicionada se já existir uma com o mesmo nome
        if main_key != lookup_key:
            df_enriched = df_enriched.drop(columns=[lookup_key])

        self.logger.info(f"Salvando o dataframe enriquecido em: {output_file}")
        df_enriched.to_csv(output_file, index=False)

        status = {
            "main_file_rows": len(df_main),
            "lookup_file_rows": len(df_lookup),
            "enriched_file_rows": len(df_enriched),
            "output_file_path": output_file
        }
        self.logger.info(f"Processo de enriquecimento concluído. Status: {status}")

        return status

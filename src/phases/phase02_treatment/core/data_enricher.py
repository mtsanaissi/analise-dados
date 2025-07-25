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

        Carrega os arquivos, valida as colunas e executa a junção.
        Se forem encontradas chaves duplicadas no arquivo de consulta, emite um aviso,
        preenche as colunas correspondentes com valores nulos para as chaves afetadas
        e continua o processo sem interrupção.

        Returns:
            Dict[str, Any]: Um dicionário de status resumindo o resultado da operação.

        Raises:
            ValueError: Se chaves de configuração estiverem faltando ou se as colunas
                        de junção não forem encontradas nos respectivos arquivos.
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

        # Identifica as chaves duplicadas e emite um aviso com a contagem.
        # A verificação de duplicatas agora serve para avisar e tratar os dados, não para interromper o processo.
        if df_lookup[lookup_key].duplicated().any():
            duplicated_keys = df_lookup[df_lookup[lookup_key].duplicated()][lookup_key]
            count = duplicated_keys.nunique()
            warning_message = f"Valores duplicados encontrados na coluna de junção '{lookup_key}': {count}."
            self.logger.warning(warning_message)

            # Para as linhas com chaves duplicadas no df_main, define as colunas a serem adicionadas como nulas.
            # Isso evita que o merge falhe ou produza resultados incorretos.
            keys_to_nullify = duplicated_keys.unique()
            for col in columns_to_add:
                if col not in df_main.columns:
                     # Garante que a coluna exista antes de tentar atribuir valores.
                    df_main[col] = pd.NA
                df_main.loc[df_main[main_key].isin(keys_to_nullify), col] = pd.NA

            # Cria uma versão do df_lookup sem as duplicatas para o merge, mantendo a primeira ocorrência.
            # Isso garante que o merge não crie linhas extras no dataframe principal.
            df_lookup_deduplicated = df_lookup.drop_duplicates(subset=[lookup_key], keep='first')
        else:
            # Se não houver duplicatas, o df_lookup original é usado.
            df_lookup_deduplicated = df_lookup
            self.logger.info("Nenhuma duplicata encontrada. Executando a junção.")

        # Realiza a junção usando o df_lookup sem duplicatas.
        # As linhas no df_main que correspondem a chaves originalmente duplicadas
        # não encontrarão correspondência aqui, preservando os nulos definidos anteriormente.
        df_enriched = pd.merge(
            df_main,
            df_lookup_deduplicated[columns_to_add + [lookup_key]],
            left_on=main_key,
            right_on=lookup_key,
            how=join_how,
            suffixes=('', '_lookup') # Adiciona sufixo para evitar conflito de colunas
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

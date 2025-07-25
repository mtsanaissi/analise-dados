import os
import pandas as pd
import argparse
import json
import logging
from src.utils import find_files, save_df_to_csv
from src.connectors.factory import get_data_loader
from .core.problematic_value_extractor import extract_values
from .core.value_corrector import apply_corrections
from .core.column_transformer import transform_columns
from .core.data_enricher import DataEnricher


def run_treatment_phase(data_project_path, extra_args):
    """
    Orquestra a fase de tratamento dos dados.
    """
    parser = argparse.ArgumentParser(
        description="Argumentos para a fase de tratamento.")
    parser.add_argument("--enrich-data",
                        dest="enrich_config_path",
                        metavar="PATH",
                        help="Caminho para o arquivo de configuração JSON para o enriquecimento de dados. Se especificado, apenas a tarefa de enriquecimento será executada.")
    args = parser.parse_args(extra_args)

    logging.info("--- Iniciando Fase 02: Tratamento ---")

    if args.enrich_config_path:
        logging.info(
            f"Modo de enriquecimento de dados ativado. Carregando configuração de: {args.enrich_config_path}")
        try:
            config_path = os.path.abspath(args.enrich_config_path)
            config_dir = os.path.dirname(config_path)

            with open(config_path, 'r', encoding='utf-8') as f:
                enrich_config = json.load(f)

            # Resolve caminhos relativos para absolutos
            for key in ['main_file', 'lookup_file', 'output_file']:
                if key in enrich_config:
                    enrich_config[key] = os.path.join(
                        config_dir, enrich_config[key])

            enricher = DataEnricher(enrich_config)
            status = enricher.enrich_data()
            logging.info(
                f"Enriquecimento de dados concluído com sucesso. Status: {status}")
        except FileNotFoundError:
            logging.error(
                f"Arquivo de configuração de enriquecimento não encontrado em: {args.enrich_config_path}")
        except json.JSONDecodeError:
            logging.error(
                f"Erro ao decodificar o arquivo JSON de configuração: {args.enrich_config_path}")
        except Exception as e:
            logging.error(
                f"Ocorreu um erro durante o enriquecimento de dados: {e}", exc_info=True)

        logging.info(
            "--- Fase 02: Tratamento (Apenas Enriquecimento) Concluída ---")
        return

    # Encontrar todos os arquivos de dados suportados
    supported_extensions = ["csv", "json", "xlsx"]
    files_to_process = find_files(data_project_path, supported_extensions)

    if not files_to_process:
        logging.warning("Nenhum arquivo de dados encontrado para tratamento.")
        return

    # Diretório para salvar os arquivos tratados
    treated_dir = os.path.join(data_project_path, "treated")
    os.makedirs(treated_dir, exist_ok=True)

    # Mapa de correções (exemplo, pode ser carregado de um arquivo)
    # TODO: Externalizar o mapa de correções
    corrections_map = {
        "valor_problematico_1": "valor_corrigido_1",
        "valor_problematico_2": "valor_corrigido_2"
    }

    for file_path in files_to_process:
        try:
            logging.info(f"Processando arquivo: {os.path.basename(file_path)}")

            # 1. Carregar dados usando a fábrica de conectores
            connector = get_data_loader(file_path)
            df = connector.read()

            if df is None:
                logging.warning(f"  -> Falha ao carregar o arquivo.")
                continue

            # 2. Extrair valores problemáticos (opcional, pode ser usado para gerar um relatório)
            problematic_values = extract_values(df)
            if problematic_values:
                logging.info(
                    f"  -> Valores problemáticos encontrados: {problematic_values}")

            # 3. Aplicar correções de valor
            df = apply_corrections(df, corrections_map)

            # 4. Transformar colunas (ex: remover coluna 'Total')
            df = transform_columns(df)

            # 5. Salvar o DataFrame tratado como CSV
            output_filename = os.path.splitext(os.path.basename(file_path))[
                0] + "_treated.csv"
            output_path = os.path.join(treated_dir, output_filename)
            save_df_to_csv(df, output_path)

            logging.info(f"  -> Arquivo tratado salvo em: {output_path}")

        except Exception as e:
            logging.error(
                f"  -> Erro ao processar o arquivo {os.path.basename(file_path)}: {e}", exc_info=True)

    logging.info("--- Fase 02: Tratamento Concluída ---")

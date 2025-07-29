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
from .core.data_concatenator import DataConcatenator
from .core.reporting import generate_json_report, generate_html_report


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
    parser.add_argument("--concatenate-data",
                        dest="concatenate_config_path",
                        metavar="PATH",
                        help="Caminho para o arquivo de configuração JSON para a concatenação de dados. Se especificado, apenas a tarefa de concatenação será executada.")
    parser.add_argument("--report-output",
                        choices=['json', 'html'],
                        default='json',
                        help="Formato do relatório de saída (padrão: json).")
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

    if args.concatenate_config_path:
        logging.info(
            f"Modo de concatenação de dados ativado. Carregando configuração de: {args.concatenate_config_path}")
        try:
            config_path = os.path.abspath(args.concatenate_config_path)
            config_dir = os.path.dirname(config_path)

            with open(config_path, 'r', encoding='utf-8') as f:
                concat_config = json.load(f)

            # Resolve caminhos relativos para absolutos
            for key in ['input_folder', 'output_file']:
                if key in concat_config:
                    concat_config[key] = os.path.join(
                        config_dir, concat_config[key])

            concatenator = DataConcatenator(concat_config)
            concatenator.concatenate_files()
            logging.info("Concatenação de dados concluída com sucesso.")

        except FileNotFoundError:
            logging.error(
                f"Arquivo de configuração de concatenação não encontrado em: {args.concatenate_config_path}")
        except json.JSONDecodeError:
            logging.error(
                f"Erro ao decodificar o arquivo JSON de configuração: {args.concatenate_config_path}")
        except Exception as e:
            logging.error(
                f"Ocorreu um erro durante a concatenação de dados: {e}", exc_info=True)

        logging.info(
            "--- Fase 02: Tratamento (Apenas Concatenação) Concluída ---")
        return

    # Encontrar todos os arquivos de dados suportados
    supported_extensions = ["csv", "json", "xlsx"]
    all_files = find_files(data_project_path, supported_extensions)

    # Ignorar arquivos de relatório
    files_to_process = [
        f for f in all_files
        if not (f.endswith('_report.json') or f.endswith('_report.html'))
    ]

    if not files_to_process:
        logging.warning("Nenhum arquivo de dados encontrado para tratamento.")
        return

    # Diretório para salvar os arquivos tratados
    treated_dir = os.path.join(data_project_path, "treated")
    os.makedirs(treated_dir, exist_ok=True)

    # Estrutura de dados para o relatório
    report_data = {
        "summary": {"total_files": 0, "processed_successfully": 0, "failed": 0},
        "details": []
    }

    # Mapa de correções (exemplo, pode ser carregado de um arquivo)
    # TODO: Externalizar o mapa de correções
    corrections_map = {
        "valor_problematico_1": "valor_corrigido_1",
        "valor_problematico_2": "valor_corrigido_2"
    }

    report_data["summary"]["total_files"] = len(files_to_process)

    for file_path in files_to_process:
        file_details = {
            "file_name": os.path.basename(file_path),
            "status": "Failed",
            "problematic_values": {},
            "applied_corrections": {}
        }

        try:
            logging.info(f"Processando arquivo: {os.path.basename(file_path)}")

            # 1. Carregar dados usando a fábrica de conectores
            connector = get_data_loader(file_path)
            df = connector.read()

            if df is None:
                logging.warning(f"  -> Falha ao carregar o arquivo.")
                report_data["summary"]["failed"] += 1
                report_data["details"].append(file_details)
                continue

            # 2. Extrair valores problemáticos
            problematic_values = extract_values(df) or {}
            file_details["problematic_values"] = problematic_values
            if problematic_values:
                logging.info(
                    f"  -> Valores problemáticos encontrados: {problematic_values}")

            # 3. Aplicar correções de valor
            df = apply_corrections(df, corrections_map)
            # Simplificação: assumindo que todas as correções no mapa são aplicadas
            file_details["applied_corrections"] = {
                k: v for k, v in corrections_map.items() if k in problematic_values
            }


            # 4. Transformar colunas
            df = transform_columns(df)

            # 5. Salvar o DataFrame tratado como CSV
            output_filename = os.path.splitext(os.path.basename(file_path))[
                0] + "_treated.csv"
            output_path = os.path.join(treated_dir, output_filename)
            save_df_to_csv(df, output_path)

            logging.info(f"  -> Arquivo tratado salvo em: {output_path}")
            file_details["status"] = "Success"
            report_data["summary"]["processed_successfully"] += 1

        except Exception as e:
            logging.error(
                f"  -> Erro ao processar o arquivo {os.path.basename(file_path)}: {e}", exc_info=True)
            report_data["summary"]["failed"] += 1

        report_data["details"].append(file_details)

    # Gerar relatório no final
    if args.report_output == 'json':
        report_path = os.path.join(treated_dir, "treatment_report.json")
        generate_json_report(report_data, report_path)
    elif args.report_output == 'html':
        report_path = os.path.join(treated_dir, "treatment_report.html")
        generate_html_report(report_data, report_path)

    logging.info("--- Fase 02: Tratamento Concluída ---")

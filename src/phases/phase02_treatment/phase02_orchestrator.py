import os
import pandas as pd
import argparse
import json
import logging
import datetime
import shutil
import yaml
from src.utils import find_files, METADATA_DIR
from src.connectors.factory import get_data_loader
from .core.data_enricher import DataEnricher
from .core.data_concatenator import DataConcatenator
from .core.reporting import generate_json_report, generate_html_report


def run_treatment_phase(data_project_path: str, extra_args: list):
    """
    Orquestra a fase de tratamento dos dados.
    """
    parser = argparse.ArgumentParser(
        description="Executa uma operação de tratamento de dados. É obrigatório escolher uma das operações abaixo.")

    operation_group = parser.add_mutually_exclusive_group(required=True)

    operation_group.add_argument("--enrich-data",
                                 dest="enrich_config_path",
                                 metavar="PATH",
                                 help="Caminho para o arquivo de configuração YAML para o enriquecimento de dados.")
    operation_group.add_argument("--concatenate-data",
                                 dest="concatenate_config_path",
                                 metavar="PATH",
                                 help="Caminho para o arquivo de configuração YAML para a concatenação de dados.")
    operation_group.add_argument("--replace-values",
                                 dest="replace_config_path",
                                 metavar="PATH",
                                 help="Caminho para o arquivo de configuração YAML para substituição de valores.")

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
            config_path = args.enrich_config_path
            if not os.path.isabs(config_path):
                config_path = os.path.join(data_project_path, "fad-config", config_path)

            config_dir = os.path.dirname(config_path)

            with open(config_path, 'r', encoding='utf-8') as f:
                enrich_config = yaml.safe_load(f)

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
                f"Arquivo de configuração de enriquecimento não encontrado em: {config_path}")
        except yaml.YAMLError:
            logging.error(
                f"Erro ao decodificar o arquivo YAML de configuração: {config_path}")
        except Exception as e:
            logging.error(
                f"Ocorreu um erro durante o enriquecimento de dados: {e}", exc_info=True)

    elif args.concatenate_config_path:
        logging.info(
            f"Modo de concatenação de dados ativado. Carregando configuração de: {args.concatenate_config_path}")
        try:
            config_path = args.concatenate_config_path
            if not os.path.isabs(config_path):
                config_path = os.path.join(data_project_path, "fad-config", config_path)

            config_dir = os.path.dirname(config_path)

            with open(config_path, 'r', encoding='utf-8') as f:
                concat_config = yaml.safe_load(f)

            for key in ['input_folder', 'output_file']:
                if key in concat_config:
                    concat_config[key] = os.path.join(
                        config_dir, concat_config[key])

            concatenator = DataConcatenator(concat_config)
            concatenator.concatenate_files()
            logging.info("Concatenação de dados concluída com sucesso.")
        except FileNotFoundError:
            logging.error(
                f"Arquivo de configuração de concatenação não encontrado em: {config_path}")
        except yaml.YAMLError:
            logging.error(
                f"Erro ao decodificar o arquivo YAML de configuração: {config_path}")
        except Exception as e:
            logging.error(
                f"Ocorreu um erro durante a concatenação de dados: {e}", exc_info=True)

    elif args.replace_config_path:
        try:
            config_path = args.replace_config_path
            if not os.path.isabs(config_path):
                config_path = os.path.join(data_project_path, "fad-config", config_path)

            with open(config_path, 'r', encoding='utf-8') as f:
                replace_config = yaml.safe_load(f)
                if not isinstance(replace_config, dict) or 'replacements' not in replace_config:
                    logging.error("Arquivo de configuração YAML é inválido. A chave 'replacements' não foi encontrada.")
                    return
        except FileNotFoundError:
            logging.error(f"Arquivo de configuração de substituição não encontrado em: {config_path}")
            return
        except yaml.YAMLError as e:
            logging.error(f"Erro ao processar o arquivo YAML: {e}")
            return

        supported_extensions = ["csv", "json", "xlsx"]
        metadata_path = os.path.join(data_project_path, METADATA_DIR)
        os.makedirs(metadata_path, exist_ok=True)

        timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        backup_dir_name = f"fad-bkp-treatment-{timestamp}"
        backup_dir_path = os.path.join(data_project_path, backup_dir_name)
        os.makedirs(backup_dir_path, exist_ok=True)
        logging.info(f"Diretório de backup criado em: {backup_dir_path}")

        files_to_process = find_files(
            data_project_path, supported_extensions, exclude_dirs=[METADATA_DIR, backup_dir_name])
        if not files_to_process:
            logging.warning(
                "Nenhum arquivo de dados encontrado para tratamento.")
            return

        report_data = {
            "summary": {"total_files": len(files_to_process), "processed_successfully": 0, "failed": 0},
            "details": []
        }

        replacement_rules = replace_config.get('replacements', [])

        for file_path in files_to_process:
            file_details = {
                "file_name": os.path.basename(file_path),
                "status": "Failed",
                "replacements_applied": []
            }
            try:
                logging.info(f"Processando arquivo: {os.path.basename(file_path)}")
                connector = get_data_loader(file_path)
                df = connector.read()
                if df is None:
                    logging.warning(f"  -> Falha ao carregar o arquivo.")
                    report_data["summary"]["failed"] += 1
                    report_data["details"].append(file_details)
                    continue

                for rule in replacement_rules:
                    existing_value = rule.get('existing_value')
                    new_value = rule.get('new_value')
                    column = rule.get('column')

                    count = 0
                    if column:
                        if column in df.columns:
                            count = (df[column] == existing_value).sum()
                            if count > 0:
                                df[column] = df[column].replace(existing_value, new_value)
                        else:
                            logging.warning(f"  -> A coluna '{column}' especificada na regra não existe no arquivo {os.path.basename(file_path)}. A regra será ignorada.")
                            continue
                    else: # Global replacement
                        count = df.apply(lambda x: (x == existing_value).sum()).sum()
                        if count > 0:
                            df.replace(existing_value, new_value, inplace=True)

                    if count > 0:
                        file_details["replacements_applied"].append({
                            "rule": rule,
                            "count": int(count)
                        })

                relative_path = os.path.relpath(file_path, data_project_path)
                backup_file_path = os.path.join(backup_dir_path, relative_path)
                os.makedirs(os.path.dirname(backup_file_path), exist_ok=True)
                shutil.move(file_path, backup_file_path)
                logging.info(f"  -> Arquivo original movido para: {backup_file_path}")

                file_extension = os.path.splitext(file_path)[1].lower()
                if file_extension == '.csv':
                    df.to_csv(file_path, index=False, sep=';', encoding='utf-8-sig')
                elif file_extension == '.xlsx':
                    df.to_excel(file_path, index=False)
                elif file_extension == '.json':
                    df.to_json(file_path, orient='records', indent=4)

                logging.info(f"  -> Arquivo tratado salvo em: {file_path}")
                file_details["status"] = "Success"
                report_data["summary"]["processed_successfully"] += 1
            except Exception as e:
                logging.error(f"  -> Erro ao processar o arquivo {os.path.basename(file_path)}: {e}", exc_info=True)
                report_data["summary"]["failed"] += 1
            report_data["details"].append(file_details)

        if args.report_output == 'json':
            report_path = os.path.join(metadata_path, "treatment_report.json")
            generate_json_report(report_data, report_path)
        elif args.report_output == 'html':
            report_path = os.path.join(metadata_path, "treatment_report.html")
            generate_html_report(report_data, report_path)

    logging.info("--- Fase 02: Tratamento Concluída ---")

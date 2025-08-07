import os
import pandas as pd
import argparse
import json
import logging
import datetime
import shutil
import yaml
import re
from src.utils import find_files, METADATA_DIR, read_yaml_config_robustly
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
    operation_group.add_argument("--find-and-replace-text",
                                     dest="text_replace_config_path",
                                     metavar="PATH",
                                     help="Caminho para o arquivo YAML para substituição de texto (substring/regex).")
    operation_group.add_argument("--strip-whitespace",
                                 action="store_true",
                                 help="Remove espaços em branco do início e do fim de todos os valores em todas as colunas.")

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
            with open(args.enrich_config_path, 'r', encoding='utf-8-sig') as f:
                enrich_config = yaml.safe_load(f)

            # Passa o caminho do projeto de dados para o enriquecedor
            enricher = DataEnricher(enrich_config, data_project_path)
            status = enricher.enrich_data()
            logging.info(
                f"Enriquecimento de dados concluído com sucesso. Status: {status}")
        except FileNotFoundError:
            logging.error(
                f"Arquivo de configuração de enriquecimento não encontrado em: {args.enrich_config_path}")
        except (yaml.YAMLError, ValueError) as e:
            logging.error(f"Erro na configuração ou processamento do YAML: {e}")
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

            with open(config_path, 'r', encoding='utf-8-sig') as f:
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

            with open(config_path, 'r', encoding='utf-8-sig') as f:
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
                connector = get_data_loader(file_path, delimiter=';')
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
                    case_sensitive = rule.get('case_sensitive', True)

                    count = 0
                    if column:
                        if column not in df.columns:
                            logging.warning(f"  -> A coluna '{column}' especificada na regra não existe no arquivo {os.path.basename(file_path)}. A regra será ignorada.")
                            continue

                        # Apenas aplica a lógica case-insensitive em colunas de texto/objeto
                        is_object_dtype = pd.api.types.is_object_dtype(df[column])

                        if not case_sensitive and is_object_dtype:
                            # Lógica Case-Insensitive para coluna específica
                            if isinstance(existing_value, list):
                                # Garante que todos os valores na lista sejam strings para lower()
                                lower_existing = [str(v).lower() for v in existing_value]
                                mask = df[column].str.lower().isin(lower_existing)
                            else:
                                mask = df[column].str.lower() == str(existing_value).lower()

                            count = int(mask.sum())
                            if count > 0:
                                df.loc[mask, column] = new_value
                        else:
                            # Lógica Case-Sensitive (comportamento original)
                            if isinstance(existing_value, list):
                                count = df[column].isin(existing_value).sum()
                            else:
                                count = (df[column] == existing_value).sum()

                            count = int(count)
                            if count > 0:
                                df[column] = df[column].replace(existing_value, new_value)
                    else: # Substituição Global
                        if not case_sensitive:
                            # Lógica Case-Insensitive para substituição global
                            total_count = 0
                            for col_name in df.select_dtypes(include=['object']).columns:
                                if isinstance(existing_value, list):
                                    lower_existing = [str(v).lower() for v in existing_value]
                                    mask = df[col_name].str.lower().isin(lower_existing)
                                else:
                                    mask = df[col_name].str.lower() == str(existing_value).lower()

                                col_count = int(mask.sum())
                                if col_count > 0:
                                    df.loc[mask, col_name] = new_value
                                    total_count += col_count
                            count = total_count
                        else:
                            # Lógica Case-Sensitive global (comportamento original)
                            if isinstance(existing_value, list):
                                count = df.apply(lambda x: x.isin(existing_value).sum()).sum()
                            else:
                                count = df.apply(lambda x: (x == existing_value).sum()).sum()

                            count = int(count)
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

    elif args.text_replace_config_path:
        config_path = args.text_replace_config_path
        if not os.path.isabs(config_path):
            config_path = os.path.join(data_project_path, "fad-config", config_path)
        text_replace_config = read_yaml_config_robustly(config_path)
        if not text_replace_config or 'text_replacements' not in text_replace_config:
            logging.error("Arquivo de configuração YAML para substituição de texto é inválido ou não foi encontrado.")
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

        replacement_rules = text_replace_config.get('text_replacements', [])

        for file_path in files_to_process:
            file_details = {
                "file_name": os.path.basename(file_path),
                "status": "Failed",
                "replacements_applied": []
            }
            try:
                logging.info(f"Processando arquivo: {os.path.basename(file_path)}")
                connector = get_data_loader(file_path, delimiter=';')
                df = connector.read()
                if df is None:
                    logging.warning(f"  -> Falha ao carregar o arquivo.")
                    report_data["summary"]["failed"] += 1
                    report_data["details"].append(file_details)
                    continue

                for rule in replacement_rules:
                    pattern = rule.get('pattern')
                    new_value = rule.get('new_value')
                    column = rule.get('column')
                    is_regex = rule.get('is_regex', False)
                    case_sensitive = rule.get('case_sensitive', True)

                    if not all([pattern, new_value, column]):
                        logging.warning(f"Regra de substituição de texto incompleta: {rule}. Pulando.")
                        continue

                    count = 0
                    if column in df.columns:
                        if pd.api.types.is_object_dtype(df[column]):
                            # Define os parâmetros com base na sensibilidade ao caso e se é regex
                            if is_regex:
                                flags = re.IGNORECASE if not case_sensitive else 0
                                # O parâmetro 'case' é ignorado pelo pandas quando regex=True, então usamos 'flags'
                                count = df[column].str.contains(pattern, regex=True, flags=flags, na=False).sum()
                                if count > 0:
                                    df[column] = df[column].str.replace(pattern, new_value, regex=True, flags=flags)
                            else:
                                # Para não-regex, o parâmetro 'case' controla a sensibilidade
                                count = df[column].str.contains(pattern, regex=False, case=case_sensitive, na=False).sum()
                                if count > 0:
                                    df[column] = df[column].str.replace(pattern, new_value, regex=False, case=case_sensitive)
                        else:
                            logging.warning(f"  -> A coluna '{column}' não é do tipo texto/objeto no arquivo {os.path.basename(file_path)}. A regra será ignorada.")
                            continue
                    else:
                        logging.warning(f"  -> A coluna '{column}' especificada na regra não existe no arquivo {os.path.basename(file_path)}. A regra será ignorada.")
                        continue

                    if count > 0:
                        file_details["replacements_applied"].append({
                            "rule": rule,
                            "count": int(count)
                        })

                if not file_details["replacements_applied"]:
                    logging.info(f"  -> Nenhuma substituição de texto aplicada para o arquivo {os.path.basename(file_path)}.")
                    file_details["status"] = "Success (No changes)"
                    report_data["summary"]["processed_successfully"] += 1
                    report_data["details"].append(file_details)
                    continue

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

    elif args.strip_whitespace:
        logging.info("Modo de remoção de espaços em branco ativado.")
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

        for file_path in files_to_process:
            file_details = {
                "file_name": os.path.basename(file_path),
                "status": "Failed",
                "changes_made": False
            }
            try:
                logging.info(f"Processando arquivo: {os.path.basename(file_path)}")
                # Forçar todas as colunas a serem lidas como texto (str)
                connector = get_data_loader(file_path, delimiter=';', dtype=str)
                df = connector.read()
                if df is None:
                    logging.warning(f"  -> Falha ao carregar o arquivo.")
                    report_data["summary"]["failed"] += 1
                    report_data["details"].append(file_details)
                    continue

                df_original = df.copy()

                # Limpa os nomes das colunas (espaços e aspas)
                df.columns = df.columns.str.strip().str.strip('"')

                # Aplicar .str.strip() em todas as colunas de dados (espaços e aspas)
                for col in df.columns:
                    if df[col].dtype == 'object':
                        df[col] = df[col].str.strip().str.strip('"')

                if not df.equals(df_original) or not df.columns.equals(df_original.columns):
                    file_details["changes_made"] = True
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
                else:
                    logging.info(f"  -> Nenhum espaço em branco encontrado para remover no arquivo {os.path.basename(file_path)}.")

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

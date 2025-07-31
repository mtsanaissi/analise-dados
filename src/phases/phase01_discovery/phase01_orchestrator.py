# -*- coding: utf-8 -*-

import logging
import os
from src.utils import find_files, METADATA_DIR
from src.phases.phase01_discovery.core.encoding_detector import process_file_encoding
from src.phases.phase01_discovery.core.data_volume_analyzer import analyze_data_volume
from src.phases.phase01_discovery.core.data_integrity_checker import analyze_data_integrity, detect_problematic_chars
from src.phases.phase01_discovery.file_type_specific.csv.delimiter_detector import detect_csv_delimiter
from src.phases.phase01_discovery.file_type_specific.csv.column_consistency_checker import check_csv_structures
from src.phases.phase01_discovery.file_type_specific.json.schema_validator import validate_json_schema
from src.phases.phase01_discovery.file_type_specific.excel.sheet_analyzer import analyze_excel_sheets
from src.phases.phase01_discovery.core.reporting import generate_html_report

import argparse
import json
import yaml
import numpy as np
from .interactive_visualizer import display_interactive_report


class NpEncoder(json.JSONEncoder):
    """
    Codificador JSON personalizado para lidar com tipos de dados NumPy.
    Converte tipos NumPy em tipos nativos do Python para serialização.
    """

    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, np.floating):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return super(NpEncoder, self).default(obj)


def run_discovery_phase(data_project_path, extra_args, extensions=['csv', 'xlsx', 'xls', 'json', 'txt'], recursive=True):
    """
    Orquestra todas as ferramentas da Fase 1: Descoberta e Diagnóstico.
    Retorna um relatório consolidado de todas as análises.
    """
    parser = argparse.ArgumentParser(
        description="Argumentos para a fase de descoberta.")
    parser.add_argument(
        "-o", "--output-format", type=str, default="text",
        choices=['text', 'interactive'],
        help="Formato da saída para a fase de descoberta (text, interactive)."
    )
    parser.add_argument(
        "--report-output", type=str, default="json",
        choices=['json', 'html'],
        help="Formato do arquivo de relatório (json, html)."
    )
    parser.add_argument(
        "--compare-fields",
        action="store_true",
        help="Habilita a comparação de campos/colunas entre arquivos do mesmo tipo."
    )
    parser.add_argument(
        "--generate-char-cleanup-config",
        metavar="OUTPUT_PATH",
        help="Verifica todos os arquivos em busca de caracteres problemáticos (ex: de controle, de substituição) e gera um arquivo de configuração YAML no caminho especificado, que pode ser usado na Fase 2 para limpeza."
    )
    args = parser.parse_args(extra_args)

    if args.output_format == 'interactive':
        logging.getLogger().setLevel(logging.WARNING)
    else:
        logging.getLogger().setLevel(logging.INFO)

    logging.info(
        f"Iniciando Fase 1: Descoberta e Diagnóstico para {data_project_path}")

    metadata_path = os.path.join(data_project_path, METADATA_DIR)
    os.makedirs(metadata_path, exist_ok=True)

    discovered_files = find_files(
        data_project_path, extensions, recursive, exclude_dirs=[METADATA_DIR])

    if not discovered_files:
        logging.warning("Nenhum arquivo encontrado para análise.")
        return {"status": "success", "message": "Nenhum arquivo encontrado para análise.", "results": {}}

    results = {
        "encoding_analysis": [],
        "data_volume_analysis": {},
        "data_integrity_analysis": {},
        "csv_delimiter_analysis": [],
        "csv_column_consistency_analysis": {},
        "json_schema_validation": [],
        "excel_sheet_analysis": [],
        "field_comparison_analysis": []
    }

    reference_columns = {'csv': None, 'json': None, 'excel': None}

    # --- Análises Gerais ---
    logging.info("--- Executando Análises Gerais ---")
    results["encoding_analysis"] = [
        process_file_encoding(fp) for fp in discovered_files]
    results["data_volume_analysis"] = analyze_data_volume(discovered_files)
    results["data_integrity_analysis"] = analyze_data_integrity(
        data_project_path, extensions, recursive)

    # --- Análises Específicas por Tipo de Arquivo ---
    csv_files = [f for f in discovered_files if f.lower().endswith('.csv')]
    json_files = [f for f in discovered_files if f.lower().endswith('.json')]
    excel_files = [
        f for f in discovered_files if f.lower().endswith(('.xlsx', '.xls'))]

    if csv_files:
        logging.info("--- Executando Análises de CSV ---")
        detected_delimiters = {}
        sorted_csv_files = sorted(csv_files)
        for fp in sorted_csv_files:
            delimiter_result = detect_csv_delimiter(fp)
            results["csv_delimiter_analysis"].append(
                {"file": os.path.basename(fp), "result": delimiter_result})
            # CUSTOMIZAR: Adicionar verificação para o caso de erro na detecção
            if "delimiter" in delimiter_result:
                detected_delimiters[fp] = delimiter_result["delimiter"]

            if args.compare_fields:
                # Importa a função aqui para evitar dependência circular
                from .file_type_specific.csv.column_consistency_checker import get_csv_headers
                delimiter = detected_delimiters.get(fp)
                current_headers = get_csv_headers(fp, delimiter=delimiter)
                if reference_columns['csv'] is None:
                    reference_columns['csv'] = current_headers
                    comparison_result = {"file": os.path.basename(
                        fp), "status": "referencia"}
                else:
                    are_equal = set(current_headers) == set(
                        reference_columns['csv'])
                    missing_columns = list(
                        set(reference_columns['csv']) - set(current_headers))
                    extra_columns = list(
                        set(current_headers) - set(reference_columns['csv']))
                    comparison_result = {
                        "file": os.path.basename(fp),
                        "status": "igual" if are_equal else "diferente",
                        "missing_columns": missing_columns,
                        "extra_columns": extra_columns
                    }
                results["field_comparison_analysis"].append(comparison_result)
        consistency_results = check_csv_structures(data_project_path, detected_delimiters_map=detected_delimiters)
        if "results" in consistency_results:
            results["csv_column_consistency_analysis"] = consistency_results["results"]

        # Mesclar resultados da verificação de consistência com a comparação de campos
        if "results" in consistency_results:
            for res in consistency_results.get("results", []):
                # Encontrar a comparação de campo correspondente
                comp_found = False
                for comp in results["field_comparison_analysis"]:
                    if comp.get("file") == res.get("file"):
                        comp_found = True
                        # Se a verificação de consistência encontrou um problema, atualize o status
                        if res.get("status") != "OK":
                            comp["status"] = res.get("status", comp.get("status"))
                            comp["details"] = res.get("details", comp.get("details"))
                        break
                # Se não houver uma entrada de comparação de campo (improvável), adicione-a
                if not comp_found:
                    results["field_comparison_analysis"].append(res)

    if json_files:
        logging.info("--- Executando Análises de JSON ---")
        for fp in json_files:
            results["json_schema_validation"].append(
                {"file": os.path.basename(fp), "result": validate_json_schema(fp)})
            if args.compare_fields:
                from .file_type_specific.json.schema_validator import get_json_keys
                current_keys = get_json_keys(fp)
                if reference_columns['json'] is None:
                    reference_columns['json'] = current_keys
                    comparison_result = {"file": os.path.basename(
                        fp), "status": "referencia"}
                else:
                    are_equal = set(current_keys) == set(
                        reference_columns['json'])
                    missing_fields = list(
                        set(reference_columns['json']) - set(current_keys))
                    extra_fields = list(
                        set(current_keys) - set(reference_columns['json']))
                    comparison_result = {
                        "file": os.path.basename(fp),
                        "status": "igual" if are_equal else "diferente",
                        "missing_fields": missing_fields,
                        "extra_fields": extra_fields
                    }
                results["field_comparison_analysis"].append(comparison_result)

    if excel_files:
        logging.info("--- Executando Análises de Excel ---")
        for fp in excel_files:
            results["excel_sheet_analysis"].append(
                {"file": os.path.basename(fp), "result": analyze_excel_sheets(fp)})
            if args.compare_fields:
                from .file_type_specific.excel.sheet_analyzer import get_excel_columns
                current_columns = get_excel_columns(fp)
                if reference_columns['excel'] is None:
                    reference_columns['excel'] = current_columns
                    comparison_result = {"file": os.path.basename(
                        fp), "status": "referencia"}
                else:
                    are_equal = set(current_columns) == set(
                        reference_columns['excel'])
                    missing_columns = list(
                        set(reference_columns['excel']) - set(current_columns))
                    extra_columns = list(
                        set(current_columns) - set(reference_columns['excel']))
                    comparison_result = {
                        "file": os.path.basename(fp),
                        "status": "igual" if are_equal else "diferente",
                        "missing_columns": missing_columns,
                        "extra_columns": extra_columns
                    }
                results["field_comparison_analysis"].append(comparison_result)

    logging.info("Fase 1: Descoberta e Diagnóstico concluída.")

    results_wrapper = {"status": "success",
                       "message": "Fase de Descoberta e Diagnóstico concluída com sucesso.", "detailed_results": results}

    if args.output_format == 'interactive':
        display_interactive_report(results_wrapper)

    if args.report_output == 'json':
        output_filename = "discovery_report.json"
        output_path = os.path.join(metadata_path, output_filename)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(results_wrapper, f, indent=4,
                      ensure_ascii=False, cls=NpEncoder)
        logging.info(f"Relatório da Fase 1 salvo em: {output_path}")
    elif args.report_output == 'html':
        output_filename = "discovery_report.html"
        output_path = os.path.join(metadata_path, output_filename)
        generate_html_report(results_wrapper['detailed_results'], output_path)
        logging.info(f"Relatório da Fase 1 salvo em: {output_path}")

    if args.generate_char_cleanup_config:
        logging.info("--- Gerando Configuração de Limpeza de Caracteres ---")

        # Mapeia o encoding de cada arquivo para fácil acesso
        encoding_map = {
            os.path.basename(item['file_path']): item.get('encoding', 'utf-8')
            for item in results.get('encoding_analysis', [])
        }

        master_problematic_chars = set()
        for file_path in discovered_files:
            file_name = os.path.basename(file_path)
            encoding = encoding_map.get(file_name, 'utf-8')

            # Garante que o encoding não seja None
            if not encoding:
                encoding = 'utf-8'

            try:
                # Usa o encoding detectado para verificar os caracteres
                found_chars = detect_problematic_chars(file_path, encoding)
                master_problematic_chars.update(found_chars)
            except Exception as e:
                logging.error(f"Não foi possível verificar o arquivo {file_path} para caracteres problemáticos: {e}")

        if master_problematic_chars:
            logging.info(f"Caracteres problemáticos encontrados: {master_problematic_chars}")

            # Estrutura de dados para o arquivo YAML
            cleanup_config = {
                'replacements': [
                    {'existing_value': char, 'new_value': ''}
                    for char in sorted(list(master_problematic_chars)) # Ordena para consistência
                ]
            }

            output_path = args.generate_char_cleanup_config
            try:
                with open(output_path, 'w', encoding='utf-8') as f:
                    # Adiciona comentário no topo do arquivo
                    f.write("# Arquivo de configuração gerado automaticamente para limpeza de caracteres.\n")
                    # Usa allow_unicode para preservar caracteres e default_flow_style=False para o formato de bloco
                    yaml.dump(cleanup_config, f, allow_unicode=True, default_flow_style=False, sort_keys=False)

                logging.info(f"Arquivo de configuração para limpeza de caracteres salvo em: {output_path}")

            except Exception as e:
                logging.error(f"Falha ao salvar o arquivo de configuração YAML em {output_path}: {e}")
        else:
            logging.info("Nenhum caractere problemático foi encontrado nos arquivos analisados.")

    return results_wrapper

# -*- coding: utf-8 -*-

import logging
import os
from src.utils import find_files
from src.phases.phase01_discovery.core.encoding_detector import process_file_encoding
from src.phases.phase01_discovery.core.data_volume_analyzer import analyze_data_volume
from src.phases.phase01_discovery.core.data_integrity_checker import analyze_data_integrity
from src.phases.phase01_discovery.file_type_specific.csv.delimiter_detector import detect_csv_delimiter
from src.phases.phase01_discovery.file_type_specific.csv.column_consistency_checker import check_csv_structures
from src.phases.phase01_discovery.file_type_specific.json.schema_validator import validate_json_schema
from src.phases.phase01_discovery.file_type_specific.excel.sheet_analyzer import analyze_excel_sheets
from src.phases.phase01_discovery.core.reporting import generate_html_report

import argparse
import json
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
    args = parser.parse_args(extra_args)

    if args.output_format == 'interactive':
        logging.getLogger().setLevel(logging.WARNING)
    else:
        logging.getLogger().setLevel(logging.INFO)

    logging.info(
        f"Iniciando Fase 1: Descoberta e Diagnóstico para {data_project_path}")

    discovered_files = find_files(
        data_project_path, extensions, recursive, exclude_patterns=['*_report.json', '*_report.html'])

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

        # Overwrite field comparison if consistency check already found differences
        if "results" in consistency_results:
            for res in consistency_results["results"]:
                for comp in results["field_comparison_analysis"]:
                    if comp["file"] == res["file"] and res["status"] != "OK":
                        comp["status"] = res["status"]
                        comp["details"] = res["details"]

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
        output_path = os.path.join(data_project_path, output_filename)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(results_wrapper, f, indent=4,
                      ensure_ascii=False, cls=NpEncoder)
        logging.info(f"Relatório da Fase 1 salvo em: {output_path}")
    elif args.report_output == 'html':
        output_filename = "discovery_report.html"
        output_path = os.path.join(data_project_path, output_filename)
        generate_html_report(results_wrapper['detailed_results'], output_path)
        logging.info(f"Relatório da Fase 1 salvo em: {output_path}")

    return results_wrapper

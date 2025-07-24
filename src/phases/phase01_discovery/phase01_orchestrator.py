# -*- coding: utf-8 -*-

import logging
import os
from utils import find_files
from phases.phase01_discovery.core.encoding_detector import process_file_encoding
from phases.phase01_discovery.core.data_volume_analyzer import analyze_data_volume
from phases.phase01_discovery.core.data_integrity_checker import analyze_data_integrity
from phases.phase01_discovery.file_type_specific.csv.delimiter_detector import detect_csv_delimiter
from phases.phase01_discovery.file_type_specific.csv.column_consistency_checker import check_csv_structures
from phases.phase01_discovery.file_type_specific.json.schema_validator import validate_json_schema
from phases.phase01_discovery.file_type_specific.excel.sheet_analyzer import analyze_excel_sheets

def run_discovery_phase(data_project_path, extensions=['csv', 'xlsx', 'xls', 'json', 'txt'], recursive=True, output_format='text', compare_fields: bool = False):
    """
    Orquestra todas as ferramentas da Fase 1: Descoberta e Diagnóstico.
    Retorna um relatório consolidado de todas as análises.
    """
    logging.info(f"Iniciando Fase 1: Descoberta e Diagnóstico para {data_project_path}")

    discovered_files = find_files(data_project_path, extensions, recursive, exclude_patterns=['*_report.json'])

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
    results["encoding_analysis"] = [process_file_encoding(fp) for fp in discovered_files]
    results["data_volume_analysis"] = analyze_data_volume(discovered_files)
    results["data_integrity_analysis"] = analyze_data_integrity(data_project_path, extensions, recursive)

    # --- Análises Específicas por Tipo de Arquivo ---
    csv_files = [f for f in discovered_files if f.lower().endswith('.csv')]
    json_files = [f for f in discovered_files if f.lower().endswith('.json')]
    excel_files = [f for f in discovered_files if f.lower().endswith(('.xlsx', '.xls'))]

    if csv_files:
        logging.info("--- Executando Análises de CSV ---")
        for fp in csv_files:
            results["csv_delimiter_analysis"].append({"file": os.path.basename(fp), "result": detect_csv_delimiter(fp)})
            if compare_fields:
                # Importa a função aqui para evitar dependência circular
                from .file_type_specific.csv.column_consistency_checker import get_csv_headers
                current_headers = get_csv_headers(fp)
                if reference_columns['csv'] is None:
                    reference_columns['csv'] = current_headers
                    comparison_result = {"file": os.path.basename(fp), "status": "referencia"}
                else:
                    are_equal = set(current_headers) == set(reference_columns['csv'])
                    missing_columns = list(set(reference_columns['csv']) - set(current_headers))
                    extra_columns = list(set(current_headers) - set(reference_columns['csv']))
                    comparison_result = {
                        "file": os.path.basename(fp),
                        "status": "igual" if are_equal else "diferente",
                        "missing_columns": missing_columns,
                        "extra_columns": extra_columns
                    }
                results["field_comparison_analysis"].append(comparison_result)
        results["csv_column_consistency_analysis"] = check_csv_structures(data_project_path)

    if json_files:
        logging.info("--- Executando Análises de JSON ---")
        for fp in json_files:
            results["json_schema_validation"].append({"file": os.path.basename(fp), "result": validate_json_schema(fp)})
            if compare_fields:
                from .file_type_specific.json.schema_validator import get_json_keys
                current_keys = get_json_keys(fp)
                if reference_columns['json'] is None:
                    reference_columns['json'] = current_keys
                    comparison_result = {"file": os.path.basename(fp), "status": "referencia"}
                else:
                    are_equal = set(current_keys) == set(reference_columns['json'])
                    missing_fields = list(set(reference_columns['json']) - set(current_keys))
                    extra_fields = list(set(current_keys) - set(reference_columns['json']))
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
            results["excel_sheet_analysis"].append({"file": os.path.basename(fp), "result": analyze_excel_sheets(fp)})
            if compare_fields:
                from .file_type_specific.excel.sheet_analyzer import get_excel_columns
                current_columns = get_excel_columns(fp)
                if reference_columns['excel'] is None:
                    reference_columns['excel'] = current_columns
                    comparison_result = {"file": os.path.basename(fp), "status": "referencia"}
                else:
                    are_equal = set(current_columns) == set(reference_columns['excel'])
                    missing_columns = list(set(reference_columns['excel']) - set(current_columns))
                    extra_columns = list(set(current_columns) - set(reference_columns['excel']))
                    comparison_result = {
                        "file": os.path.basename(fp),
                        "status": "igual" if are_equal else "diferente",
                        "missing_columns": missing_columns,
                        "extra_columns": extra_columns
                    }
                results["field_comparison_analysis"].append(comparison_result)

    logging.info("Fase 1: Descoberta e Diagnóstico concluída.")

    results_wrapper = {"status": "success", "message": "Fase de Descoberta e Diagnóstico concluída com sucesso.", "detailed_results": results}

    if output_format == 'interactive':
        from .interactive_visualizer import display_interactive_report
        display_interactive_report(results_wrapper)

    return results_wrapper

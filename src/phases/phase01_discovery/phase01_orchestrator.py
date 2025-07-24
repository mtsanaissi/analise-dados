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

def run_discovery_phase(data_project_path, extensions=['csv', 'xlsx', 'xls', 'json', 'txt'], recursive=True, output_format='text'):
    """
    Orquestra todas as ferramentas da Fase 1: Descoberta e Diagnóstico.
    Retorna um relatório consolidado de todas as análises.
    """
    logging.info(f"Iniciando Fase 1: Descoberta e Diagnóstico para {data_project_path}")

    exclude_patterns = ['*_report.json', '*_report.html']
    discovered_files = find_files(data_project_path, extensions, recursive, exclude_patterns=exclude_patterns)

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
        "excel_sheet_analysis": []
    }

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
        results["csv_column_consistency_analysis"] = check_csv_structures(data_project_path)

    if json_files:
        logging.info("--- Executando Análises de JSON ---")
        for fp in json_files:
            results["json_schema_validation"].append({"file": os.path.basename(fp), "result": validate_json_schema(fp)})

    if excel_files:
        logging.info("--- Executando Análises de Excel ---")
        for fp in excel_files:
            results["excel_sheet_analysis"].append({"file": os.path.basename(fp), "result": analyze_excel_sheets(fp)})

    logging.info("Fase 1: Descoberta e Diagnóstico concluída.")

    results_wrapper = {"status": "success", "message": "Fase de Descoberta e Diagnóstico concluída com sucesso.", "detailed_results": results}

    if output_format == 'interactive':
        from .interactive_visualizer import display_interactive_report
        display_interactive_report(results_wrapper)

    return results_wrapper

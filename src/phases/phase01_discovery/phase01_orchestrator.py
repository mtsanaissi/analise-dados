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

    # Define padrões de exclusão para não analisar os próprios relatórios gerados
    exclude_patterns = ['*_report.json', '*_report.html']
    discovered_files = find_files(data_project_path, extensions, recursive, exclude_patterns=exclude_patterns)

    if not discovered_files:
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

    # 1. Análise de Encoding
    logging.info("--- Executando Análise de Encoding ---")
    for file_path in discovered_files:
        try:
            encoding_result = process_file_encoding(file_path)
            results["encoding_analysis"].append(encoding_result)
            logging.info(f"  {os.path.basename(file_path)}: {encoding_result['message']}")
        except Exception as e:
            logging.error(f"Falha na Análise de Encoding para {os.path.basename(file_path)}: {e}")
            results["encoding_analysis"].append({"file": os.path.basename(file_path), "status": "error", "message": str(e)})

    # 2. Análise de Volume de Dados
    logging.info("--- Executando Análise de Volume de Dados ---")
    try:
        volume_result = analyze_data_volume(discovered_files)
        results["data_volume_analysis"] = volume_result
        logging.info(f"Resumo de Volume: {volume_result['message']}")
    except Exception as e:
        logging.error(f"Falha na Análise de Volume de Dados: {e}")
        results["data_volume_analysis"] = {"status": "error", "message": str(e)}

    # 3. Análise de Integridade de Dados
    logging.info("--- Executando Análise de Integridade de Dados ---")
    try:
        integrity_result = analyze_data_integrity(data_project_path, extensions, recursive)
        results["data_integrity_analysis"] = integrity_result
        logging.info(f"Resumo de Integridade: {integrity_result['message']}")
    except Exception as e:
        logging.error(f"Falha na Análise de Integridade de Dados: {e}")
        results["data_integrity_analysis"] = {"status": "error", "message": str(e)}

    # 4. Análise de Delimitador CSV (apenas para arquivos CSV)
    csv_files = [f for f in discovered_files if f.lower().endswith('.csv')]
    if csv_files:
        logging.info("--- Executando Análise de Delimitador CSV ---")
        for file_path in csv_files:
            try:
                delimiter_result = detect_csv_delimiter(file_path)
                results["csv_delimiter_analysis"].append({"file": os.path.basename(file_path), "result": delimiter_result})
                logging.info(f"  {os.path.basename(file_path)}: Delimitador detectado: {delimiter_result.get('delimiter', 'N/A')}")
            except Exception as e:
                logging.error(f"Falha na Análise de Delimitador CSV para {os.path.basename(file_path)}: {e}")
                results["csv_delimiter_analysis"].append({"file": os.path.basename(file_path), "status": "error", "message": str(e)})

    # 5. Análise de Consistência de Colunas CSV (apenas para arquivos CSV)
    if csv_files:
        logging.info("--- Executando Análise de Consistência de Colunas CSV ---")
        try:
            column_consistency_result = check_csv_structures(data_project_path)
            results["csv_column_consistency_analysis"] = column_consistency_result
            logging.info(f"  Consistência de Colunas CSV: {column_consistency_result['message']}")
        except Exception as e:
            logging.error(f"Falha na Análise de Consistência de Colunas CSV: {e}")
            results["csv_column_consistency_analysis"] = {"status": "error", "message": str(e)}

    # 6. Análise de Esquema JSON (apenas para arquivos JSON)
    json_files = [f for f in discovered_files if f.lower().endswith('.json')]
    if json_files:
        logging.info("--- Executando Análise de Esquema JSON ---")
        for file_path in json_files:
            try:
                schema_result = validate_json_schema(file_path)
                results["json_schema_validation"].append({"file": os.path.basename(file_path), "result": schema_result})
                logging.info(f"  {os.path.basename(file_path)}: Status da validação do esquema: {schema_result['status']}")
            except Exception as e:
                logging.error(f"Falha na Análise de Esquema JSON para {os.path.basename(file_path)}: {e}")
                results["json_schema_validation"].append({"file": os.path.basename(file_path), "status": "error", "message": str(e)})

    # 7. Análise de Planilhas Excel (apenas para arquivos XLSX)
    excel_files = [f for f in discovered_files if f.lower().endswith(('.xlsx', '.xls'))]
    if excel_files:
        logging.info("--- Executando Análise de Planilhas Excel ---")
        for file_path in excel_files:
            try:
                sheet_analysis_result = analyze_excel_sheets(file_path)
                results["excel_sheet_analysis"].append({"file": os.path.basename(file_path), "result": sheet_analysis_result})
                logging.info(f"  {os.path.basename(file_path)}: Status da análise de planilhas: {sheet_analysis_result['status']}")
            except Exception as e:
                logging.error(f"Falha na Análise de Planilhas Excel para {os.path.basename(file_path)}: {e}")
                results["excel_sheet_analysis"].append({"file": os.path.basename(file_path), "status": "error", "message": str(e)})

    logging.info("\nFase 1: Descoberta e Diagnóstico concluída.")

    results_wrapper = {"status": "success", "message": "Fase de Descoberta e Diagnóstico concluída com sucesso.", "detailed_results": results}

    if output_format == 'interactive':
        from .interactive_visualizer import display_interactive_report
        display_interactive_report(results_wrapper)

    return results_wrapper
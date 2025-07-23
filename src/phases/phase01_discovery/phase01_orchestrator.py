# -*- coding: utf-8 -*-

import os
from utils import find_files
from phases.phase01_discovery.core.encoding_detector import process_file_encoding
from phases.phase01_discovery.core.data_volume_analyzer import analyze_data_volume
from phases.phase01_discovery.core.data_integrity_checker import analyze_data_integrity
from phases.phase01_discovery.file_type_specific.csv.delimiter_detector import detect_csv_delimiter
from phases.phase01_discovery.file_type_specific.csv.column_consistency_checker import check_csv_structures
from phases.phase01_discovery.file_type_specific.json.schema_validator import validate_json_schema
from phases.phase01_discovery.file_type_specific.excel.sheet_analyzer import analyze_excel_sheets
from phases.phase01_discovery.core.data_profiler import analyze_data_profiling


def run_discovery_phase(data_project_path, extensions=['csv', 'xlsx', 'xls', 'json', 'txt'], recursive=True):
    """
    Orquestra todas as ferramentas da Fase 1: Descoberta e Diagnóstico.
    Retorna um relatório consolidado de todas as análises.
    """
    print(f"Iniciando Fase 1: Descoberta e Diagnóstico para {data_project_path}")

    discovered_files = find_files(data_project_path, extensions, recursive)
    if not discovered_files:
        return {"status": "success", "message": "Nenhum arquivo encontrado para análise.", "results": {}}

    results = {
        "encoding_analysis": [],
        "data_volume_analysis": {},
        "data_integrity_analysis": {},
        "csv_delimiter_analysis": [],
        "csv_column_consistency_analysis": {},
        "json_schema_validation": [],
        "excel_sheet_analysis": [],
        "data_profiling_analysis": []
    }

    # 1. Análise de Encoding
    print("\n--- Executando Análise de Encoding ---")
    for file_path in discovered_files:
        encoding_result = process_file_encoding(file_path)
        results["encoding_analysis"].append(encoding_result)
        print(f"  {os.path.basename(file_path)}: {encoding_result['message']}")

    # 2. Análise de Volume de Dados
    print("\n--- Executando Análise de Volume de Dados ---")
    volume_result = analyze_data_volume(discovered_files)
    results["data_volume_analysis"] = volume_result
    print(f"  Resumo de Volume: {volume_result['message']}")

    # 3. Análise de Integridade de Dados
    print("\n--- Executando Análise de Integridade de Dados ---")
    integrity_result = analyze_data_integrity(data_project_path, extensions, recursive)
    results["data_integrity_analysis"] = integrity_result
    print(f"  Resumo de Integridade: {integrity_result['message']}")

    # 4. Análise de Delimitador CSV (apenas para arquivos CSV)
    print("\n--- Executando Análise de Delimitador CSV ---")
    csv_files = [f for f in discovered_files if f.lower().endswith('.csv')]
    for file_path in csv_files:
        delimiter_result = detect_csv_delimiter(file_path)
        results["csv_delimiter_analysis"].append({"file": os.path.basename(file_path), "result": delimiter_result})
        print(f"  {os.path.basename(file_path)}: Delimitador detectado: {delimiter_result.get('delimiter', 'N/A')}")

    # 5. Análise de Consistência de Colunas CSV (apenas para arquivos CSV)
    print("\n--- Executando Análise de Consistência de Colunas CSV ---")
    if csv_files:
        column_consistency_result = check_csv_structures(data_project_path)
        results["csv_column_consistency_analysis"] = column_consistency_result
        print(f"  Consistência de Colunas CSV: {column_consistency_result['message']}")
    else:
        print("  Nenhum arquivo CSV encontrado para análise de consistência de colunas.")

    # 6. Análise de Esquema JSON (apenas para arquivos JSON)
    print("\n--- Executando Análise de Esquema JSON ---")
    json_files = [f for f in discovered_files if f.lower().endswith('.json')]
    for file_path in json_files:
        schema_result = validate_json_schema(file_path)
        results["json_schema_validation"].append({"file": os.path.basename(file_path), "result": schema_result})
        print(f"  {os.path.basename(file_path)}: Status da validação do esquema: {schema_result['status']}")

    # 7. Análise de Planilhas Excel (apenas para arquivos XLSX)
    print("\n--- Executando Análise de Planilhas Excel ---")
    excel_files = [f for f in discovered_files if f.lower().endswith('.xlsx')]
    for file_path in excel_files:
        sheet_analysis_result = analyze_excel_sheets(file_path)
        results["excel_sheet_analysis"].append({"file": os.path.basename(file_path), "result": sheet_analysis_result})
        print(f"  {os.path.basename(file_path)}: Status da análise de planilhas: {sheet_analysis_result['status']}")

    # 8. Perfilamento de Dados
    print("\n--- Executando Perfilamento de Dados ---")
    profiling_result = analyze_data_profiling(data_project_path, extensions, recursive)
    results["data_profiling_analysis"] = profiling_result
    print(f"  Perfilamento de Dados: {profiling_result['message']}")


    print("\nFase 1: Descoberta e Diagnóstico concluída.")
    return {"status": "success", "message": "Fase de Descoberta e Diagnóstico concluída com sucesso.", "detailed_results": results}
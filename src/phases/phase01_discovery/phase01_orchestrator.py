# -*- coding: utf-8 -*-

import logging
import os
from src.utils import find_files, METADATA_DIR
from src.phases.phase01_discovery.core.encoding_detector import detect_encoding
from src.phases.phase01_discovery.core.data_volume_analyzer import analyze_data_volume
from src.phases.phase01_discovery.core.data_integrity_checker import analyze_data_integrity, detect_problematic_chars
from src.phases.phase01_discovery.file_type_specific.csv.delimiter_detector import detect_csv_delimiter
from src.phases.phase01_discovery.file_type_specific.csv.column_consistency_checker import check_csv_structures
from src.phases.phase01_discovery.file_type_specific.json.schema_validator import validate_json_schema
from src.phases.phase01_discovery.file_type_specific.excel.sheet_analyzer import analyze_excel_sheets, get_excel_columns
from src.phases.phase01_discovery.core.reporting import generate_html_report
from src.phases.phase01_discovery.core.data_profiler import profile_dataframe
from src.connectors.factory import CsvConnector, XlsxConnector
import pandas as pd

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


def run_discovery_logic(
    data_project_path: str,
    extensions: list = ['csv', 'xlsx', 'xls', 'json', 'txt'],
    recursive: bool = True,
    output_format: str = "text",
    report_output: str = "json",
    compare_fields: bool = False,
    compare_types: bool = False,
    generate_char_cleanup_config: str = None
):
    """
    Orquestra todas as ferramentas da Fase 1: Descoberta e Diagnóstico.
    Retorna um dicionário estruturado com os resultados.
    """
    if output_format == 'interactive':
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
        return {"status": "success", "message": "Nenhum arquivo encontrado para análise.", "report_path": None}

    results = {
        "encoding_analysis": [],
        "data_volume_analysis": {},
        "data_integrity_analysis": {},
        "csv_delimiter_analysis": [],
        "csv_column_consistency_analysis": {},
        "json_schema_validation": [],
        "excel_sheet_analysis": [],
        "field_comparison_analysis": [],
        "type_consistency_analysis": []
    }

    reference_columns = {'csv': None, 'json': None, 'excel': None}
    reference_types = {'csv': None, 'json': None, 'excel': None}

    # --- Análises Gerais ---
    logging.info("--- Executando Análises Gerais ---")
    results["encoding_analysis"] = [
        detect_encoding(fp) for fp in discovered_files]
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
            if "delimiter" in delimiter_result:
                detected_delimiters[fp] = delimiter_result["delimiter"]

            if compare_fields:
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

            if compare_types:
                base_name = os.path.basename(fp)
                df = None
                try:
                    delimiter = detected_delimiters.get(fp)
                    if not delimiter:
                        logging.warning(f"Não foi possível determinar o delimitador para {base_name}. Pulando comparação de tipos.")
                        results["type_consistency_analysis"].append({"file": base_name, "status": "erro_delimitador"})
                        continue

                    connector = CsvConnector(file_path=fp, delimiter=delimiter)
                    df = connector.read()

                    if df is None or df.empty:
                        results["type_consistency_analysis"].append({"file": base_name, "status": "vazio_ou_nao_suportado"})
                        continue

                    profile = profile_dataframe(df)
                    current_types = {item['nome_coluna']: item['tipo_inferido'] for item in profile}

                    if reference_types['csv'] is None:
                        reference_types['csv'] = current_types
                        results["type_consistency_analysis"].append({"file": base_name, "status": "referencia"})
                    else:
                        reference = reference_types['csv']
                        inconsistencies = []
                        common_columns = set(reference.keys()) & set(current_types.keys())

                        for col in common_columns:
                            if reference[col] != current_types[col]:
                                inconsistencies.append({
                                    "column": col,
                                    "reference_type": reference[col],
                                    "current_type": current_types[col]
                                })

                        if inconsistencies:
                            results["type_consistency_analysis"].append({
                                "file": base_name,
                                "status": "inconsistente",
                                "inconsistencies": inconsistencies
                            })
                        else:
                            results["type_consistency_analysis"].append({"file": base_name, "status": "consistente"})

                except Exception as e:
                    logging.error(f"Erro ao processar o arquivo {base_name} para comparação de tipos: {e}")
                    results["type_consistency_analysis"].append({"file": base_name, "status": "erro_leitura", "details": str(e)})

        consistency_results = check_csv_structures(data_project_path, detected_delimiters_map=detected_delimiters)
        if "results" in consistency_results:
            results["csv_column_consistency_analysis"] = consistency_results["results"]

        if "results" in consistency_results:
            for res in consistency_results.get("results", []):
                comp_found = False
                for comp in results["field_comparison_analysis"]:
                    if comp.get("file") == res.get("file"):
                        comp_found = True
                        if res.get("status") != "OK":
                            comp["status"] = res.get("status", comp.get("status"))
                            comp["details"] = res.get("details", comp.get("details"))
                        break
                if not comp_found:
                    results["field_comparison_analysis"].append(res)

    if json_files:
        logging.info("--- Executando Análises de JSON ---")
        json_files.sort()
        for fp in json_files:
            results["json_schema_validation"].append(
                {"file": os.path.basename(fp), "result": validate_json_schema(fp)})
            if compare_fields:
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

            if compare_types:
                base_name = os.path.basename(fp)
                df = None
                try:
                    try:
                        df = pd.read_json(fp, lines=True)
                    except (ValueError, TypeError):
                        df = pd.read_json(fp)

                    if df is None or df.empty:
                        results["type_consistency_analysis"].append({"file": base_name, "status": "vazio_ou_nao_suportado"})
                        continue

                    profile = profile_dataframe(df)
                    current_types = {item['nome_coluna']: item['tipo_inferido'] for item in profile}

                    if reference_types['json'] is None:
                        reference_types['json'] = current_types
                        results["type_consistency_analysis"].append({"file": base_name, "status": "referencia"})
                    else:
                        reference = reference_types['json']
                        inconsistencies = []
                        common_columns = set(reference.keys()) & set(current_types.keys())

                        for col in common_columns:
                            if reference[col] != current_types[col]:
                                inconsistencies.append({
                                    "column": col,
                                    "reference_type": reference[col],
                                    "current_type": current_types[col]
                                })

                        if inconsistencies:
                            results["type_consistency_analysis"].append({
                                "file": base_name,
                                "status": "inconsistente",
                                "inconsistencies": inconsistencies
                            })
                        else:
                            results["type_consistency_analysis"].append({"file": base_name, "status": "consistente"})

                except Exception as e:
                    logging.error(f"Erro ao processar o arquivo {base_name} para comparação de tipos: {e}")
                    results["type_consistency_analysis"].append({"file": base_name, "status": "erro_leitura", "details": str(e)})

    if excel_files:
        logging.info("--- Executando Análises de Excel ---")
        excel_files.sort()
        for fp in excel_files:
            base_name = os.path.basename(fp)
            try:
                with pd.ExcelFile(fp) as xls:
                    # 1. Análise de Planilhas
                    results["excel_sheet_analysis"].append(
                        {"file": base_name, "result": analyze_excel_sheets(xls)}
                    )

                    # 2. Comparação de Campos
                    if compare_fields:
                        current_columns = get_excel_columns(xls)
                        if reference_columns['excel'] is None:
                            reference_columns['excel'] = current_columns
                            comparison_result = {"file": base_name, "status": "referencia"}
                        else:
                            are_equal = set(current_columns) == set(reference_columns['excel'])
                            missing_columns = list(set(reference_columns['excel']) - set(current_columns))
                            extra_columns = list(set(current_columns) - set(reference_columns['excel']))
                            comparison_result = {
                                "file": base_name,
                                "status": "igual" if are_equal else "diferente",
                                "missing_columns": missing_columns,
                                "extra_columns": extra_columns
                            }
                        results["field_comparison_analysis"].append(comparison_result)

                    # 3. Comparação de Tipos
                    if compare_types:
                        # Lê a primeira planilha para o DataFrame
                        df = xls.parse(xls.sheet_names[0])
                        if df is None or df.empty:
                            results["type_consistency_analysis"].append({"file": base_name, "status": "vazio_ou_nao_suportado"})
                        else:
                            profile = profile_dataframe(df)
                            current_types = {item['nome_coluna']: item['tipo_inferido'] for item in profile}

                            if reference_types['excel'] is None:
                                reference_types['excel'] = current_types
                                results["type_consistency_analysis"].append({"file": base_name, "status": "referencia"})
                            else:
                                reference = reference_types['excel']
                                inconsistencies = []
                                common_columns = set(reference.keys()) & set(current_types.keys())

                                for col in common_columns:
                                    if reference[col] != current_types[col]:
                                        inconsistencies.append({
                                            "column": col,
                                            "reference_type": reference[col],
                                            "current_type": current_types[col]
                                        })

                                if inconsistencies:
                                    results["type_consistency_analysis"].append({
                                        "file": base_name,
                                        "status": "inconsistente",
                                        "inconsistencies": inconsistencies
                                    })
                                else:
                                    results["type_consistency_analysis"].append({"file": base_name, "status": "consistente"})
            except Exception as e:
                logging.error(f"Erro ao processar o arquivo Excel {base_name}: {e}")
                if compare_types:
                    results["type_consistency_analysis"].append({"file": base_name, "status": "erro_leitura", "details": str(e)})
                if compare_fields:
                     results["field_comparison_analysis"].append({"file": base_name, "status": "erro_leitura", "details": str(e)})

    logging.info("Fase 1: Descoberta e Diagnóstico concluída.")

    results_wrapper = {"status": "success",
                       "message": "Fase de Descoberta e Diagnóstico concluída com sucesso.", "detailed_results": results}

    if output_format == 'interactive':
        display_interactive_report(results_wrapper)

    output_path = None
    if report_output == 'json':
        output_filename = "discovery_report.json"
        output_path = os.path.join(metadata_path, output_filename)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(results_wrapper, f, indent=4,
                      ensure_ascii=False, cls=NpEncoder)
        logging.info(f"Relatório da Fase 1 salvo em: {output_path}")
    elif report_output == 'html':
        output_filename = "discovery_report.html"
        output_path = os.path.join(metadata_path, output_filename)
        generate_html_report(results_wrapper['detailed_results'], output_path)
        logging.info(f"Relatório da Fase 1 salvo em: {output_path}")

    if generate_char_cleanup_config:
        logging.info("--- Gerando Configuração de Limpeza de Caracteres ---")

        encoding_map = {
            os.path.basename(item['file_path']): {
                'encoding': item.get('encoding', 'utf-8'),
                'confidence': item.get('confidence', 0.0)
            }
            for item in results.get('encoding_analysis', [])
        }

        master_problematic_chars = set()
        for file_path in discovered_files:
            file_name = os.path.basename(file_path)
            encoding_info = encoding_map.get(file_name, {'encoding': 'utf-8', 'confidence': 1.0})

            confidence = encoding_info.get('confidence')
            if confidence < 0.9:
                logging.warning(f"A verificação de caracteres para o arquivo '{os.path.basename(file_path)}' foi pulada devido à baixa confiança na detecção de encoding ({confidence:.2f}). Valide o encoding manualmente.")
                continue

            encoding = encoding_info.get('encoding', 'utf-8')

            if not encoding:
                encoding = 'utf-8'

            try:
                found_chars = detect_problematic_chars(file_path, encoding)
                master_problematic_chars.update(found_chars)
            except Exception as e:
                logging.error(f"Não foi possível verificar o arquivo {file_path} para caracteres problemáticos: {e}")

        if master_problematic_chars:
            logging.info(f"Caracteres problemáticos encontrados: {master_problematic_chars}")

            cleanup_config = {
                'replacements': [
                    {'existing_value': char, 'new_value': ''}
                    for char in sorted(list(master_problematic_chars))
                ]
            }

            output_path_yaml = generate_char_cleanup_config
            try:
                with open(output_path_yaml, 'w', encoding='utf-8') as f:
                    f.write("# Arquivo de configuração gerado automaticamente para limpeza de caracteres.\n")
                    yaml.dump(cleanup_config, f, allow_unicode=True, default_flow_style=False, sort_keys=False)

                logging.info(f"Arquivo de configuração para limpeza de caracteres salvo em: {output_path_yaml}")

            except Exception as e:
                logging.error(f"Falha ao salvar o arquivo de configuração YAML em {output_path_yaml}: {e}")
        else:
            logging.info("Nenhum caractere problemático foi encontrado nos arquivos analisados.")

    return {
        "status": "success",
        "message": f"Fase de Descoberta e Diagnóstico concluída com sucesso. Relatório salvo em: {output_path}",
        "report_path": output_path
    }

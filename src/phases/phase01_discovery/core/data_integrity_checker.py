# -*- coding: utf-8 -*-

import os
import pandas as pd
import chardet
import csv
import json
import codecs  # Para leitura com tratamento de erros de encoding
from typing import Set
from src.utils import find_files  # Importa a função centralizada


# Amostra de 1MB
def detect_problematic_chars(file_path: str, encoding_to_try: str, sample_size_bytes: int = 1024*1024) -> Set[str]:
    """
    Verifica uma amostra do arquivo por caracteres de controle não padrão ou
    caracteres de substituição Unicode (U+FFFD) e retorna um conjunto de
    caracteres problemáticos únicos.

    Args:
        file_path (str): O caminho para o arquivo a ser verificado.
        encoding_to_try (str): O encoding a ser usado para ler o arquivo.
        sample_size_bytes (int): O tamanho da amostra a ser lida em bytes.

    Returns:
        Set[str]: Um conjunto contendo as strings dos caracteres problemáticos únicos.
    """
    problematic_chars = set()
    control_chars_allowed = {'\t', '\n', '\r'}  # Tab, Newline, Carriage Return

    try:
        with codecs.open(file_path, 'r', encoding=encoding_to_try, errors='replace') as f:
            sample_content = f.read(sample_size_bytes)

            for char_read in sample_content:
                # Se um caractere de substituição é encontrado, o caractere original é desconhecido.
                # Adicionamos a representação do caractere de substituição para indicar o problema.
                if char_read == '\ufffd':
                    problematic_chars.add(char_read)

                # Adiciona caracteres de controle não permitidos
                if not char_read.isprintable() and char_read not in control_chars_allowed:
                    problematic_chars.add(char_read)

    except Exception:
        # Em caso de erro na leitura (que pode ser um erro de encoding não tratável pelo 'replace'),
        # não podemos determinar os caracteres. A função retornará o que encontrou até agora.
        # O ideal é que o encoding já tenha sido validado antes.
        pass

    return problematic_chars


from src.phases.phase01_discovery.file_type_specific.csv.delimiter_detector import detect_csv_delimiter

def check_csv_file(file_path):
    """
    Realiza verificações de integridade em um arquivo CSV, centralizando a detecção de formato.
    """
    report = {
        "file_path": file_path,
        "file_type": "CSV",
        "status": "Pendente",
        "details": {
            "encoding": None,
            "delimiter": None,
            "has_header": None,
            "num_columns_header": None,
            "column_consistency_issue": False,
            "is_empty": False,
            "error_message": None
        }
    }

    if os.path.getsize(file_path) == 0:
        report["details"]["is_empty"] = True
        report["status"] = "Atenção"
        report["details"]["error_message"] = "Arquivo está vazio."
        return report

    detection_result = detect_csv_delimiter(file_path)
    if "error" in detection_result:
        report["status"] = "Erro"
        report["details"]["error_message"] = detection_result["error"]
        return report

    detected_encoding = detection_result.get("encoding_used", "utf-8")
    delimiter = detection_result.get("delimiter")
    has_header = detection_result.get("has_header")

    report["details"]["encoding"] = detected_encoding
    report["details"]["delimiter"] = delimiter
    report["details"]["has_header"] = has_header

    try:
        df_sample = pd.read_csv(
            file_path,
            encoding=detected_encoding,
            sep=delimiter,
            nrows=100,
            header=0 if has_header else None,
            on_bad_lines='skip'
        )

        if df_sample.empty and os.path.getsize(file_path) > 0:
             report["details"]["error_message"] = "Pandas leu um DataFrame vazio, verifique o arquivo."
             report["status"] = "Atenção"
        else:
            report["details"]["num_columns_header"] = len(df_sample.columns)
            report["status"] = "OK"

    except pd.errors.EmptyDataError:
        report["status"] = "Atenção"
        report["details"]["error_message"] = "Pandas: Arquivo CSV está vazio ou não contém dados."
        report["details"]["is_empty"] = True
    except pd.errors.ParserError as e:
        report["status"] = "Erro"
        report["details"]["error_message"] = f"Pandas ParserError: {str(e)}. Inconsistência no número de colunas."
        report["details"]["column_consistency_issue"] = True
    except UnicodeDecodeError as e:
        report["status"] = "Erro"
        report["details"]["error_message"] = f"Pandas UnicodeDecodeError: {str(e)}. Encoding '{detected_encoding}' pode estar incorreto."
    except Exception as e:
        report["status"] = "Erro"
        report["details"]["error_message"] = f"Pandas: Erro ao ler amostra do CSV: {str(e)}"

    if report["status"] == "Pendente":
        report["status"] = "Atenção" if report["details"]["error_message"] else "OK"

    return report


def check_excel_file(file_path):
    """
    Realiza verificações de integridade em um arquivo Excel (XLS, XLSX).
    """
    report = {
        "file_path": file_path,
        "file_type": "Excel",
        "status": "Pendente",
        "details": {
            "is_empty": False,
            "sheets_info": [],
            "error_message": None
        }
    }

    if os.path.getsize(file_path) < 20:
        report["details"]["is_empty"] = True
        report["status"] = "Atenção"
        report["details"]["error_message"] = "Arquivo Excel parece estar vazio ou é muito pequeno."
        return report

    try:
        xls = pd.ExcelFile(file_path)
        sheet_names = xls.sheet_names
        if not sheet_names:
            report["status"] = "Atenção"
            report["details"]["error_message"] = "Arquivo Excel não contém planilhas."
            return report

        all_sheets_ok = True
        for sheet_name in sheet_names:
            sheet_info = {"name": sheet_name, "readable": False,
                          "num_columns": None, "error_message": None}
            try:
                df_sheet_sample = pd.read_excel(
                    xls, sheet_name=sheet_name, nrows=5)
                sheet_info["readable"] = True
                sheet_info["num_columns"] = df_sheet_sample.shape[1]
                if df_sheet_sample.empty and os.path.getsize(file_path) > 1024:
                    sheet_info["error_message"] = "Amostra da planilha lida como vazia, mas o arquivo é grande."
                    all_sheets_ok = False
            except Exception as e_sheet:
                sheet_info[
                    "error_message"] = f"Erro ao ler amostra da planilha '{sheet_name}': {str(e_sheet)}"
                all_sheets_ok = False
            report["details"]["sheets_info"].append(sheet_info)

        report["status"] = "OK" if all_sheets_ok else "Atenção"

    except Exception as e:
        report["status"] = "Erro"
        report["details"][
            "error_message"] = f"Falha ao abrir ou processar arquivo Excel: {str(e)}"
        return report

    if report["status"] == "Pendente":
        report["status"] = "OK"

    return report


def check_json_file(file_path):
    """
    Realiza verificações de integridade em um arquivo JSON.
    """
    report = {
        "file_path": file_path,
        "file_type": "JSON",
        "status": "Pendente",
        "details": {
            "encoding": None,
            "encoding_confidence": None,
            "json_type": "Indeterminado",
            "is_empty": False,
            "error_message": None
        }
    }

    if os.path.getsize(file_path) == 0:
        report["details"]["is_empty"] = True
        report["status"] = "Atenção"
        report["details"]["error_message"] = "Arquivo JSON está vazio."
        return report

    try:
        with open(file_path, 'rb') as f:
            raw_data = f.read(1024 * 20)
            if not raw_data:
                report["details"]["is_empty"] = True
                report["status"] = "Atenção"
                report["details"]["error_message"] = "Arquivo JSON não contém dados para análise de encoding."
                return report
            detection = chardet.detect(raw_data)
            report["details"]["encoding"] = detection['encoding']
            report["details"]["encoding_confidence"] = detection['confidence']
    except Exception as e:
        report["status"] = "Erro"
        report["details"][
            "error_message"] = f"Falha ao tentar detectar encoding do JSON: {str(e)}"
        return report

    detected_encoding = report["details"]["encoding"] if report["details"]["encoding_confidence"] > 0.7 else 'utf-8'
    if detected_encoding is None:
        detected_encoding = 'utf-8'
        report["details"]["encoding"] = "utf-8 (fallback)"
        report["details"]["encoding_confidence"] = 0.0

    try:
        with codecs.open(file_path, 'r', encoding=detected_encoding, errors='strict') as f:
            json.load(f)
            report["details"]["json_type"] = "Padrão (objeto/array único)"
            report["status"] = "OK"
    except json.JSONDecodeError:
        try:
            with codecs.open(file_path, 'r', encoding=detected_encoding, errors='strict') as f:
                line_count = 0
                json_lines_valid = True
                for line in f:
                    line_count += 1
                    if line.strip():
                        json.loads(line)
                    if line_count > 100 and json_lines_valid:
                        break
                if line_count > 0 and json_lines_valid:
                    report["details"]["json_type"] = "JSON Lines (múltiplos objetos JSON, um por linha)"
                    report["status"] = "OK"
                elif line_count == 0:
                    report["details"]["json_type"] = "Inválido (vazio ou apenas linhas em branco)"
                    report["status"] = "Atenção"
                    report["details"]["error_message"] = "Arquivo JSON contém apenas linhas vazias."
                else:
                    report["details"]["json_type"] = "Inválido (provavelmente não é JSON Lines ou contém linhas malformadas)"
                    report["status"] = "Erro"
                    report["details"]["error_message"] = "JSONDecodeError: Falha ao parsear como JSON padrão ou JSON Lines."
        except Exception as e_lines:
            report["details"]["json_type"] = "Inválido"
            report["status"] = "Erro"
            report["details"][
                "error_message"] = f"Erro ao processar como JSON Lines: {str(e_lines)}"
    except UnicodeDecodeError as e_unicode:
        report["status"] = "Erro"
        report["details"]["json_type"] = "Inválido"
        report["details"][
            "error_message"] = f"UnicodeDecodeError: Encoding '{detected_encoding}' incorreto para JSON. Detalhes: {str(e_unicode)}"
    except Exception as e_gen:
        report["status"] = "Erro"
        report["details"]["json_type"] = "Inválido"
        report["details"]["error_message"] = f"Erro ao processar JSON: {str(e_gen)}"

    if report["status"] == "Pendente":
        report["status"] = "OK" if not report["details"]["error_message"] else "Atenção"

    return report


def analyze_data_integrity(root_directory, extensions=['csv', 'xlsx', 'json', 'xls'], recursive=True):
    """
    Orquestra a verificação de integridade para múltiplos arquivos em um diretório.
    Retorna uma lista de relatórios de integridade para cada arquivo.
    """
    if not os.path.isdir(root_directory):
        return {"status": "error", "message": f"O diretório '{root_directory}' não existe ou não é um diretório.", "reports": []}

    discovered_files = find_files(
        root_directory, extensions, recursive, exclude_patterns=['*_report.json'])

    if not discovered_files:
        return {"status": "success", "message": "Nenhum arquivo encontrado com os critérios especificados.", "reports": []}

    all_reports = []
    for file_path in discovered_files:
        _, file_ext_with_dot = os.path.splitext(file_path)
        extension = file_ext_with_dot.lstrip('.').lower()

        report = None
        if extension == 'csv':
            report = check_csv_file(file_path)
        elif extension in ['xlsx', 'xls']:
            report = check_excel_file(file_path)
        elif extension == 'json':
            report = check_json_file(file_path)

        if report:
            all_reports.append(report)

    return {"status": "success", "message": "Verificação de integridade concluída.", "reports": all_reports}

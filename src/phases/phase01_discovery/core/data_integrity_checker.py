# -*- coding: utf-8 -*-

import os
import pandas as pd
import chardet
import csv
import json
import codecs  # Para leitura com tratamento de erros de encoding
from utils import find_files  # Importa a função centralizada
# from utils import has_problematic_char, read_csv_robust # Estas funções não estão no utils.py atual, vou refatorar para usar as funções internas ou remover se não forem necessárias.


# Amostra de 1MB
def detect_problematic_chars(file_path, encoding_to_try, sample_size_bytes=1024*1024):
    """
    Verifica uma amostra do arquivo por caracteres de controle não padrão ou
    caracteres de substituição Unicode (U+FFFD).
    """
    problematic_chars_found = False
    problematic_char_samples = []
    control_chars_allowed = {'	', '\n', '\r'}  # Tab, Newline, Carriage Return

    try:
        with codecs.open(file_path, 'r', encoding=encoding_to_try, errors='replace') as f:
            sample_content = f.read(sample_size_bytes // 2)

            for i, char_read in enumerate(sample_content):
                if char_read == '\ufffd':  # Caractere de substituição Unicode
                    problematic_chars_found = True
                    if len(problematic_char_samples) < 5:
                        problematic_char_samples.append(
                            f"U+FFFD na posição ~{i} (decodificação falhou)")
                    if len(problematic_char_samples) >= 5:
                        break

                if not char_read.isprintable() and char_read not in control_chars_allowed:
                    problematic_chars_found = True
                    if len(problematic_char_samples) < 5:
                        problematic_char_samples.append(
                            f"Caractere de controle não imprimível '{repr(char_read)}' (U+{ord(char_read):04X}) na posição ~{i}")
                    if len(problematic_char_samples) >= 5:
                        break

    except Exception as e:
        problematic_chars_found = True
        problematic_char_samples.append(
            f"Erro ao ler para verificar caracteres: {str(e)}")

    return problematic_chars_found, problematic_char_samples


def check_csv_file(file_path):
    """
    Realiza verificações de integridade em um arquivo CSV.
    """
    report = {
        "file_path": file_path,
        "file_type": "CSV",
        "status": "Pendente",
        "details": {
            "encoding": None,
            "encoding_confidence": None,
            "delimiter": None,
            "has_header": None,
            "num_columns_header": None,
            "column_consistency_issue": False,
            "is_empty": False,
            "problematic_chars_found": False,
            "problematic_char_samples": [],
            "error_message": None
        }
    }

    if os.path.getsize(file_path) == 0:
        report["details"]["is_empty"] = True
        report["status"] = "Atenção"
        report["details"]["error_message"] = "Arquivo está vazio."
        return report

    try:
        with open(file_path, 'rb') as f:
            raw_data = f.read(1024 * 20)
            if not raw_data:
                report["details"]["is_empty"] = True
                report["status"] = "Atenção"
                report["details"]["error_message"] = "Arquivo não contém dados suficientes para análise de encoding."
                return report

            detection = chardet.detect(raw_data)
            report["details"]["encoding"] = detection['encoding']
            report["details"]["encoding_confidence"] = detection['confidence']
    except Exception as e:
        report["status"] = "Erro"
        report["details"][
            "error_message"] = f"Falha ao tentar detectar encoding: {str(e)}"
        return report

    detected_encoding = report["details"]["encoding"] if report["details"]["encoding_confidence"] > 0.7 else 'utf-8'
    if detected_encoding is None:
        detected_encoding = 'utf-8'
        report["details"]["encoding"] = "utf-8 (fallback)"
        report["details"]["encoding_confidence"] = 0.0

    try:
        with codecs.open(file_path, 'r', encoding=detected_encoding, errors='replace') as f_csv:
            sample_lines = "".join(f_csv.readline() for _ in range(20))
            if not sample_lines.strip():
                report["status"] = "Atenção"
                report["details"]["error_message"] = "Arquivo CSV parece conter apenas linhas vazias ou muito poucas linhas para análise."
                return report

            dialect = csv.Sniffer().sniff(
                sample_lines, delimiters=[',', ';', '	', '|', ':'])
            report["details"]["delimiter"] = repr(dialect.delimiter)[1:-1]

            f_csv.seek(0)
            report["details"]["has_header"] = csv.Sniffer().has_header(
                "".join(f_csv.readline() for _ in range(5)))

            f_csv.seek(0)
            reader = csv.reader(f_csv, dialect=dialect)
            first_row = next(reader, None)
            if first_row:
                report["details"]["num_columns_header"] = len(first_row)
            else:
                report["status"] = "Atenção"
                report["details"]["error_message"] = "Não foi possível ler a primeira linha para determinar o número de colunas."
                return report

    except csv.Error as e:
        report["status"] = "Atenção"
        report["details"]["error_message"] = f"CSV Sniffer falhou: {str(e)}. Pode indicar delimitador incomum ou arquivo malformatado."
    except Exception as e:
        report["status"] = "Erro"
        report["details"][
            "error_message"] = f"Falha ao analisar CSV para delimitador/cabeçalho: {str(e)}"
        return report

    try:
        df_sample = pd.read_csv(
            file_path,
            encoding=detected_encoding,
            sep=report["details"]["delimiter"],
            nrows=100,
            header=0 if report["details"]["has_header"] else None,
            on_bad_lines='skip'
        )
        if df_sample.empty and report["details"]["num_columns_header"] is not None:
            report["details"]["error_message"] = (report["details"].get("error_message", "") +
                                                  " Pandas leu um DataFrame vazio da amostra, verifique o arquivo.").strip()
            report["status"] = "Atenção"

        report["status"] = "OK"
        if report["details"]["error_message"] and "CSV Sniffer falhou" in report["details"]["error_message"]:
            report["status"] = "Atenção"

    except pd.errors.EmptyDataError:
        report["status"] = "Atenção"
        report["details"]["error_message"] = "Pandas: Arquivo CSV está vazio ou não contém dados."
        report["details"]["is_empty"] = True
    except pd.errors.ParserError as e:
        report["status"] = "Erro"
        report["details"]["error_message"] = f"Pandas ParserError: {str(e)}. Provável inconsistência no número de colunas ou formato."
        report["details"]["column_consistency_issue"] = True
    except UnicodeDecodeError as e:
        report["status"] = "Erro"
        report["details"]["error_message"] = f"Pandas UnicodeDecodeError: {str(e)}. Encoding '{detected_encoding}' pode estar incorreto."
    except Exception as e:
        report["status"] = "Erro"
        report["details"][
            "error_message"] = f"Pandas: Erro ao ler amostra do CSV: {str(e)}"

    if report["status"] != "Erro" or "Encoding" not in report["details"]["error_message"]:
        prob_chars, prob_samples = detect_problematic_chars(
            file_path, detected_encoding)
        report["details"]["problematic_chars_found"] = prob_chars
        report["details"]["problematic_char_samples"] = prob_samples
        if prob_chars and report["status"] == "OK":
            report["status"] = "Atenção"

    if report["status"] == "Pendente":
        if report["details"]["error_message"]:
            report["status"] = "Atenção"
        else:
            report["status"] = "OK"

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
            "problematic_chars_found": False,
            "problematic_char_samples": [],
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
            "problematic_chars_found": False,
            "problematic_char_samples": [],
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

    if report["status"] != "Erro" or "Encoding" not in report["details"].get("error_message", ""):
        prob_chars, prob_samples = detect_problematic_chars(
            file_path, detected_encoding)
        report["details"]["problematic_chars_found"] = prob_chars
        report["details"]["problematic_char_samples"] = prob_samples
        if prob_chars and report["status"] == "OK":
            report["status"] = "Atenção"

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

    discovered_files = find_files(root_directory, extensions, recursive)

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

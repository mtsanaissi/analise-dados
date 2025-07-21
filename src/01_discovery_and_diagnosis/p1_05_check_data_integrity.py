# -*- coding: utf-8 -*-

# --------------------------------------------------------------------------------
# Descrição: Este script realiza uma verificação inicial da integridade e
#            estrutura de arquivos de dados (CSV, XLSX, JSON).
#            Ele verifica a legibilidade, encoding, estrutura básica
#            (delimitadores, cabeçalhos para CSV; planilhas para Excel;
#            validade para JSON) e a presença de caracteres problemáticos.
# Exemplo de uso: python p1_05_check_data_integrity.py --argumento valor
#
# Autor: Marcelo Anaissi
# Criado em: 29/05/2025
# Versão: 1.1
#
# Modificado por: Jules
# Modificado em: 21/07/2025
# Licença: MIT
# --------------------------------------------------------------------------------

import os
import argparse
import sys
import pandas as pd
import chardet
import csv
import json
import codecs  # Para leitura com tratamento de erros de encoding
from ..utils import find_files, has_problematic_char, read_csv_robust


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
            # //2 para dar margem ao tamanho do char
            sample_content = f.read(sample_size_bytes // 2)

            for i, char_read in enumerate(sample_content):
                if char_read == '\ufffd':  # Caractere de substituição Unicode
                    problematic_chars_found = True
                    if len(problematic_char_samples) < 5:  # Coleta algumas amostras
                        # Tenta pegar um contexto pequeno, mas pode ser complexo se o erro for no meio de um char multibyte
                        # Para simplificar, apenas o caractere de substituição é suficiente como indicação.
                        problematic_char_samples.append(
                            f"U+FFFD na posição ~{i} (decodificação falhou)")
                    # Não precisa checar mais após encontrar alguns, para performance
                    if len(problematic_char_samples) >= 5:
                        break

                # Verifica caracteres de controle não permitidos
                # unicodedata.category(char_read).startswith('C') poderia ser mais robusto
                # mas isprintable() é uma boa aproximação para o que é visível.
                if not char_read.isprintable() and char_read not in control_chars_allowed:
                    problematic_chars_found = True
                    if len(problematic_char_samples) < 5:
                        problematic_char_samples.append(
                            f"Caractere de controle não imprimível '{repr(char_read)}' (U+{ord(char_read):04X}) na posição ~{i}")
                    if len(problematic_char_samples) >= 5:
                        break

    except Exception as e:
        # Se a própria leitura com 'replace' falhar, é um problema sério.
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
            "num_columns_header": None,  # Número de colunas inferido do cabeçalho
            "column_consistency_issue": False,
            "is_empty": False,
            "problematic_chars_found": False,
            "problematic_char_samples": [],
            "error_message": None
        }
    }

    # 1. Arquivo Vazio
    if os.path.getsize(file_path) == 0:
        report["details"]["is_empty"] = True
        report["status"] = "Atenção"
        report["details"]["error_message"] = "Arquivo está vazio."
        return report

    # 2. Detecção de Encoding
    try:
        with open(file_path, 'rb') as f:
            raw_data = f.read(1024 * 20)  # Lê primeiros 20KB para chardet
            if not raw_data:  # Caso raro de arquivo não vazio mas sem conteúdo legível aqui
                report["details"]["is_empty"] = True  # Reclassifica
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
    if detected_encoding is None:  # Chardet pode retornar None
        detected_encoding = 'utf-8'
        report["details"]["encoding"] = "utf-8 (fallback)"
        report["details"]["encoding_confidence"] = 0.0

    # 3. Delimitador e Cabeçalho
    try:
        with codecs.open(file_path, 'r', encoding=detected_encoding, errors='replace') as f_csv:
            # Lê algumas linhas para o Sniffer
            sample_lines = "".join(f_csv.readline() for _ in range(20))
            if not sample_lines.strip():
                report["status"] = "Atenção"
                report["details"]["error_message"] = "Arquivo CSV parece conter apenas linhas vazias ou muito poucas linhas para análise."
                return report

            dialect = csv.Sniffer().sniff(
                sample_lines, delimiters=[',', ';', '\t', '|', ':'])
            report["details"]["delimiter"] = repr(dialect.delimiter)[
                1:-1]  # Remove aspas da representação

            # Reinicia o ponteiro para verificar cabeçalho
            f_csv.seek(0)
            report["details"]["has_header"] = csv.Sniffer().has_header(
                "".join(f_csv.readline() for _ in range(5)))

            # Pega o número de colunas do cabeçalho (se houver) ou da primeira linha
            f_csv.seek(0)
            reader = csv.reader(f_csv, dialect=dialect)
            first_row = next(reader, None)
            if first_row:
                report["details"]["num_columns_header"] = len(first_row)
            else:  # Arquivo com apenas uma linha e era vazia ou algo assim
                report["status"] = "Atenção"
                report["details"]["error_message"] = "Não foi possível ler a primeira linha para determinar o número de colunas."
                return report

    except csv.Error as e:  # Erro do Sniffer
        # Pode ser um CSV malformado, mas não necessariamente um erro fatal de leitura
        report["status"] = "Atenção"
        report["details"]["error_message"] = f"CSV Sniffer falhou: {str(e)}. Pode indicar delimitador incomum ou arquivo malformatado."
        # Continuar para tentar ler com Pandas
    except Exception as e:
        report["status"] = "Erro"
        report["details"][
            "error_message"] = f"Falha ao analisar CSV para delimitador/cabeçalho: {str(e)}"
        # Não tentar Pandas se a leitura básica já falhou aqui
        return report

    # 4. Consistência de Colunas (usando Pandas) e Leitura Básica
    try:
        # Tenta ler uma amostra com Pandas para ver se ele consegue com o encoding/delimitador
        # Se num_columns_header for None, Pandas tentará inferir
        df_sample = pd.read_csv(
            file_path,
            encoding=detected_encoding,
            # Pode ser None se sniffer falhou, Pandas tentará inferir
            sep=report["details"]["delimiter"],
            nrows=100,  # Lê uma amostra para verificar a estrutura
            header=0 if report["details"]["has_header"] else None,
            on_bad_lines='skip'  # Pula linhas ruins na amostra para não quebrar a verificação inicial
        )
        if df_sample.empty and report["details"]["num_columns_header"] is not None:
            report["details"]["error_message"] = (report["details"].get("error_message", "") +
                                                  " Pandas leu um DataFrame vazio da amostra, verifique o arquivo.").strip()
            report["status"] = "Atenção"

        # Para uma verificação de consistência mais profunda (opcional aqui, pois pode ser lento):
        # Tentar ler o arquivo inteiro e capturar ParserError pode ser feito,
        # mas para a "verificação inicial" vamos apenas confiar que se o Pandas leu a amostra, está "OK" por agora.
        # Uma indicação de "column_consistency_issue" pode vir de warnings do Pandas ou se nrows limitou muito
        # e um teste posterior com o dataframe completo falha.
        # Por ora, se não houve erro explícito, assumimos que está ok para esta etapa.

        report["status"] = "OK"  # Se chegou até aqui sem erros maiores
        if report["details"]["error_message"] and "CSV Sniffer falhou" in report["details"]["error_message"]:
            # Mantém Atenção se Sniffer falhou mas Pandas conseguiu
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
        # Se Pandas falhou, o status deve ser Erro ou Atenção dependendo da severidade

    # 5. Verificação de Caracteres Problemáticos (se o arquivo foi minimamente legível)
    # Só tenta se o encoding parece OK
    if report["status"] != "Erro" or "Encoding" not in report["details"]["error_message"]:
        prob_chars, prob_samples = detect_problematic_chars(
            file_path, detected_encoding)
        report["details"]["problematic_chars_found"] = prob_chars
        report["details"]["problematic_char_samples"] = prob_samples
        if prob_chars and report["status"] == "OK":
            # Rebaixa para Atenção se encontrou caracteres estranhos
            report["status"] = "Atenção"

    # Refina o status se ainda for "Pendente"
    if report["status"] == "Pendente":
        if report["details"]["error_message"]:
            # Se tem msg de erro, mas não foi crítico
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
            # Lista de dicts: {name, readable, num_columns, error_message}
            "sheets_info": [],
            # Menos comum a nível de arquivo, mais a nível de célula (Etapa 3)
            "problematic_chars_found": False,
            "problematic_char_samples": [],
            "error_message": None
        }
    }

    if os.path.getsize(file_path) < 20:  # Arquivos Excel válidos geralmente são maiores
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
                # Lê apenas as primeiras linhas para verificar a legibilidade e estrutura básica
                df_sheet_sample = pd.read_excel(
                    xls, sheet_name=sheet_name, nrows=5)
                sheet_info["readable"] = True
                sheet_info["num_columns"] = df_sheet_sample.shape[1]
                # Se o arquivo é grande e a planilha amostra vazia
                if df_sheet_sample.empty and os.path.getsize(file_path) > 1024:
                    sheet_info["error_message"] = "Amostra da planilha lida como vazia, mas o arquivo é grande."
                    all_sheets_ok = False  # Considera uma atenção
            except Exception as e_sheet:
                sheet_info[
                    "error_message"] = f"Erro ao ler amostra da planilha '{sheet_name}': {str(e_sheet)}"
                all_sheets_ok = False
            report["details"]["sheets_info"].append(sheet_info)

        report["status"] = "OK" if all_sheets_ok else "Atenção"

    # Erro ao abrir o ExcelFile (arquivo corrompido, formato errado)
    except Exception as e:
        report["status"] = "Erro"
        report["details"][
            "error_message"] = f"Falha ao abrir ou processar arquivo Excel: {str(e)}"
        # Não faz sentido checar caracteres se nem abrir conseguiu
        return report

    # Verificação de caracteres problemáticos (a nível de arquivo é menos comum aqui,
    # mas podemos tentar ler o XML interno se for XLSX, ou apenas ignorar para Excel nesta etapa)
    # Por simplicidade, vamos omitir a checagem de caracteres problemáticos para Excel na Etapa 1,
    # pois seria mais complexo e menos direto que em arquivos texto.

    # Refina o status se ainda for "Pendente"
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
            "json_type": "Indeterminado",  # 'standard', 'lines', 'invalid'
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

    # Detecção de Encoding (similar ao CSV)
    try:
        with open(file_path, 'rb') as f:
            raw_data = f.read(1024 * 20)  # Lê primeiros 20KB
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

    # Validação da Estrutura JSON
    try:
        with codecs.open(file_path, 'r', encoding=detected_encoding, errors='strict') as f:
            # Tenta carregar como JSON padrão primeiro
            json.load(f)  # Se isso passar, é um JSON standard válido
            report["details"]["json_type"] = "Padrão (objeto/array único)"
            report["status"] = "OK"
    except json.JSONDecodeError:
        # Se falhou, tenta como JSON Lines
        try:
            with codecs.open(file_path, 'r', encoding=detected_encoding, errors='strict') as f:
                line_count = 0
                json_lines_valid = True
                for line in f:
                    line_count += 1
                    if line.strip():  # Ignora linhas em branco
                        json.loads(line)  # Tenta parsear cada linha
                    if line_count > 100 and json_lines_valid:  # Limita a verificação para arquivos grandes
                        break
                if line_count > 0 and json_lines_valid:
                    report["details"]["json_type"] = "JSON Lines (múltiplos objetos JSON, um por linha)"
                    report["status"] = "OK"
                elif line_count == 0:  # Arquivo com linhas mas todas vazias
                    report["details"]["json_type"] = "Inválido (vazio ou apenas linhas em branco)"
                    report["status"] = "Atenção"
                    report["details"]["error_message"] = "Arquivo JSON contém apenas linhas vazias."
                else:  # Se json.loads falhou em alguma linha
                    report["details"]["json_type"] = "Inválido (provavelmente não é JSON Lines ou contém linhas malformadas)"
                    report["status"] = "Erro"
                    report["details"]["error_message"] = "JSONDecodeError: Falha ao parsear como JSON padrão ou JSON Lines."
        except Exception as e_lines:  # Outro erro ao tentar ler como JSON Lines
            report["details"]["json_type"] = "Inválido"
            report["status"] = "Erro"
            report["details"][
                "error_message"] = f"Erro ao processar como JSON Lines: {str(e_lines)}"
    except UnicodeDecodeError as e_unicode:
        report["status"] = "Erro"
        report["details"]["json_type"] = "Inválido"
        report["details"][
            "error_message"] = f"UnicodeDecodeError: Encoding '{detected_encoding}' incorreto para JSON. Detalhes: {str(e_unicode)}"
    except Exception as e_gen:  # Outro erro genérico ao tentar ler como JSON padrão
        report["status"] = "Erro"
        report["details"]["json_type"] = "Inválido"
        report["details"]["error_message"] = f"Erro ao processar JSON: {str(e_gen)}"

    # Verificação de Caracteres Problemáticos (se o JSON foi minimamente legível ou o encoding parece ok)
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


def main():
    parser = argparse.ArgumentParser(
        description="Verifica a integridade inicial de arquivos de dados (CSV, XLSX, JSON).",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument(
        "-d", "--root-directory",
        type=str,
        required=True,
        help="Diretório raiz para a busca dos arquivos de dados."
    )
    parser.add_argument(
        "-e", "--extensions",
        nargs='+',
        default=['csv', 'xlsx', 'json', 'xls'],  # Adicionado 'xls'
        type=str,
        help="Lista de extensões de arquivo a serem consideradas (sem o ponto inicial).\nPadrão: csv xlsx json xls"
    )
    parser.add_argument(
        "-r", "--recursive",
        action="store_true",
        help="Incluir subdiretórios na busca."
    )
    parser.add_argument(
        "-o", "--output-report",
        type=str,
        help="Caminho para salvar o relatório de integridade em formato JSON. Se não fornecido, imprime no console."
    )

    args = parser.parse_args()

    try:
        root_dir_processed = os.path.abspath(
            os.path.expanduser(args.root_directory))
    except Exception as e:
        print(
            f"Erro Crítico: Falha ao processar o caminho do diretório raiz '{args.root_directory}': {e}")
        sys.exit(1)

    print("--- Configurações da Verificação de Integridade ---")
    print(f"Diretório Raiz: {root_dir_processed}")
    print(f"Extensões Alvo: {', '.join(args.extensions)}")
    print(f"Buscar em Subdiretórios: {'Sim' if args.recursive else 'Não'}")
    print("-------------------------------------------------\n")

    print(f"Iniciando busca de arquivos em: {root_dir_processed}")
    if args.recursive:
        print("Buscando recursivamente em subdiretórios...")
    else:
        print("Buscando apenas no diretório raiz (sem subdiretórios)...")

    discovered_files = find_data_files(
        root_dir_processed, args.extensions, args.recursive)

    if not discovered_files:
        print("Nenhum arquivo encontrado com os critérios especificados.")
        sys.exit(0)

    print(
        f"\nEncontrados {len(discovered_files)} arquivo(s). Iniciando verificações de integridade...\n")

    all_reports = []
    apt_files_count = 0

    for file_path in discovered_files:
        print(f"Verificando arquivo: {file_path} ...")
        _, file_ext_with_dot = os.path.splitext(file_path)
        extension = file_ext_with_dot.lstrip('.').lower()

        report = None
        if extension == 'csv':
            report = check_csv_file(file_path)
        # Trata xls e xlsx da mesma forma para esta etapa
        elif extension in ['xlsx', 'xls']:
            report = check_excel_file(file_path)
        elif extension == 'json':
            report = check_json_file(file_path)
        else:
            print(
                f"  Extensão '{extension}' não suportada para verificação de integridade neste script.")
            continue  # Pula para o próximo arquivo

        if report:
            all_reports.append(report)
            print(f"  Status: {report['status']}")
            if report['details'].get('error_message'):
                print(
                    f"    Detalhes do Erro/Atenção: {report['details']['error_message']}")
            if report['details'].get('problematic_chars_found'):
                print(
                    f"    Caracteres Problemáticos Encontrados: Sim. Amostras: {report['details']['problematic_char_samples']}")
            # Consideramos 'Atenção' como apto, mas com ressalvas
            if report['status'] == "OK" or report['status'] == "Atenção":
                apt_files_count += 1

    print("\n--- Resumo da Verificação de Integridade ---")
    print(f"Total de arquivos processados: {len(all_reports)}")
    # Pendente não deveria ocorrer no final
    status_counts = {"OK": 0, "Atenção": 0, "Erro": 0, "Pendente": 0}
    for r in all_reports:
        status_counts[r['status']] = status_counts.get(r['status'], 0) + 1

    for status, count in status_counts.items():
        if count > 0:
            print(f"  Arquivos com status '{status}': {count}")

    print(
        f"Total de arquivos considerados aptos para próximas etapas (status OK ou Atenção): {apt_files_count}")

    if args.output_report:
        try:
            with open(args.output_report, 'w', encoding='utf-8') as f_out:
                json.dump(all_reports, f_out, indent=4, ensure_ascii=False)
            print(f"\nRelatório de integridade salvo em: {args.output_report}")
        except Exception as e:
            print(f"\nErro ao salvar relatório em '{args.output_report}': {e}")
    else:
        # Opcional: Imprimir detalhes de cada relatório se não for salvar em arquivo
        # print("\n--- Detalhes dos Relatórios ---")
        # for rep_idx, rep_item in enumerate(all_reports):
        #     print(f"\nRelatório {rep_idx+1}/{len(all_reports)}: {rep_item['file_path']}")
        #     print(f"  Tipo: {rep_item['file_type']}, Status: {rep_item['status']}")
        #     for key, value in rep_item['details'].items():
        #         if value or key in ["is_empty", "problematic_chars_found"]: # Mostra mesmo se for False para chaves importantes
        #             if key == "sheets_info" and isinstance(value, list):
        #                 print(f"    {key.replace('_', ' ').capitalize()}:")
        #                 for sheet_val in value:
        #                     print(f"      - {sheet_val}")
        #             elif key == "problematic_char_samples" and isinstance(value, list) and value:
        #                  print(f"    {key.replace('_', ' ').capitalize()}:")
        #                  for sample_val in value:
        #                     print(f"      - {sample_val}")
        #             else:
        #                 print(f"    {key.replace('_', ' ').capitalize()}: {value}")
        pass  # Os prints durante o loop já dão um bom feedback

    print("\nVerificação de integridade concluída.")


if __name__ == "__main__":
    main()

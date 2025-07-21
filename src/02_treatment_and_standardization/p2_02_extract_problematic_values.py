#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ----------------------------------------------------------------------------
# Script: extract_problematic_csv_values.py
# Autor: Marcelo Anaissi
# Data: 29/05/2025
# Versão: 1.1 (Adicionado delimitador CSV parametrizável)
# Licença: (Se aplicável)
# Descrição: Este script varre arquivos CSV em um diretório e subdiretórios,
#            identifica caracteres problemáticos nas células e extrai
#            os valores completos dessas células para um arquivo JSON.
#            Há um tratamento especial para concatenar colunas "Cidade" e "UF".
#            O delimitador CSV pode ser especificado pelo usuário.
# ----------------------------------------------------------------------------

import os
import argparse
import sys
import pandas as pd
import json
from ..utils import find_files, has_problematic_char, read_csv_robust


def process_csv_file(file_path, csv_delimiter, column_name_cidade="Cidade", column_name_uf="UF"):
    """
    Processa um arquivo CSV para encontrar valores com caracteres problemáticos.
    """
    problematic_entries_for_file = {}
    file_had_problems = False

    df = read_csv_robust(file_path, delimiter=csv_delimiter)
    if df is None:
        return None

    column_name_cidade_lower = column_name_cidade.lower()
    column_name_uf_lower = column_name_uf.lower()

    # 3. Iterar sobre as células
    for col_name_original_case in df.columns:
        col_name_lower = col_name_original_case.lower()

        for row_idx, value in df[col_name_original_case].items():
            if has_problematic_char(value):
                file_had_problems = True
                display_value = str(value)

                if col_name_lower == column_name_cidade_lower:
                    uf_value = ""
                    found_uf_col_original_case = None
                    for orig_h_name in df.columns:
                        if orig_h_name.lower() == column_name_uf_lower:
                            found_uf_col_original_case = orig_h_name
                            break

                    if found_uf_col_original_case and found_uf_col_original_case in df.columns:
                        # Usar .get() para evitar KeyError se a linha não existir (improvável com .items())
                        uf_value = str(
                            df.get(found_uf_col_original_case, {}).get(row_idx, "")).strip()

                    if uf_value:
                        display_value = f"{str(value).strip()} - {uf_value}"
                    else:
                        display_value = str(value).strip()

                if col_name_original_case not in problematic_entries_for_file:
                    problematic_entries_for_file[col_name_original_case] = []

                if display_value not in problematic_entries_for_file[col_name_original_case]:
                    problematic_entries_for_file[col_name_original_case].append(
                        display_value)

    if file_had_problems:
        return problematic_entries_for_file
    else:
        return None


def main():
    parser = argparse.ArgumentParser(
        description="Extrai valores com caracteres problemáticos de arquivos CSV para um JSON.",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument(
        "-d", "--root-directory",
        type=str,
        default="../data/fix/",
        help="Diretório raiz para a busca dos arquivos CSV.\nPadrão: ../data/fix/"
    )
    parser.add_argument(
        "-r", "--recursive",
        action="store_true",
        default=True,
        help="Incluir subdiretórios na busca. Padrão: True."
    )
    parser.add_argument(
        "--no-recursive",
        action="store_false",
        dest="recursive",
        help="Não incluir subdiretórios na busca."
    )
    parser.add_argument(
        "-o", "--output-json",
        type=str,
        default="problematic_csv_values.json",
        help="Caminho para salvar o arquivo JSON com os resultados.\nPadrão: problematic_csv_values.json"
    )
    parser.add_argument(
        "--delimiter",
        type=str,
        default=";",  # Padrão é ponto e vírgula
        help="Delimitador utilizado nos arquivos CSV.\nPadrão: ';' (ponto e vírgula).\nUse '\\t' para TAB."
    )
    parser.add_argument(
        "--col-cidade",
        type=str,
        default="Cidade",
        help="Nome da coluna que representa a cidade (case-insensitive na busca).\nPadrão: Cidade"
    )
    parser.add_argument(
        "--col-uf",
        type=str,
        default="UF",
        help="Nome da coluna que representa o estado/UF (case-insensitive na busca).\nPadrão: UF"
    )

    args = parser.parse_args()

    # Trata o delimitador TAB se fornecido como '\t'
    actual_delimiter = args.delimiter
    if actual_delimiter == '\\t':
        actual_delimiter = '\t'

    try:
        root_dir_processed = os.path.abspath(
            os.path.expanduser(args.root_directory))
    except Exception as e:
        print(
            f"Erro Crítico: Falha ao processar o caminho do diretório raiz '{args.root_directory}': {e}")
        sys.exit(1)

    print("--- Configurações da Extração ---")
    print(f"Diretório Raiz: {root_dir_processed}")
    print(f"Buscar em Subdiretórios: {'Sim' if args.recursive else 'Não'}")
    print(f"Delimitador CSV: '{actual_delimiter}'")
    print(f"Arquivo JSON de Saída: {args.output_json}")
    print(f"Nome Coluna Cidade: {args.col_cidade}")
    print(f"Nome Coluna UF: {args.col_uf}")
    print("---------------------------------\n")

    print(f"Iniciando busca de arquivos CSV em: {root_dir_processed}")
    discovered_files = find_csv_files(root_dir_processed, args.recursive)

    if not discovered_files:
        print("Nenhum arquivo CSV encontrado com os critérios especificados.")
        sys.exit(0)

    print(
        f"\nEncontrados {len(discovered_files)} arquivo(s) CSV. Iniciando processamento...\n")

    all_problematic_data = []
    files_with_problems_count = 0

    for file_path in discovered_files:
        relative_file_path = os.path.relpath(file_path, root_dir_processed)
        print(f"Processando arquivo: {relative_file_path} ...")

        entries = process_csv_file(
            file_path, actual_delimiter, args.col_cidade, args.col_uf)

        if entries:
            files_with_problems_count += 1
            file_report = {"arquivo": relative_file_path}
            file_report.update(entries)
            all_problematic_data.append(file_report)
            print(f"  -> Encontrados problemas em {len(entries)} coluna(s).")
        else:
            print(
                f"  -> Nenhum caractere problemático encontrado ou arquivo não pôde ser processado.")

    print("\n--- Resumo da Extração ---")
    print(f"Total de arquivos CSV processados: {len(discovered_files)}")
    print(
        f"Total de arquivos CSV com caracteres problemáticos identificados: {files_with_problems_count}")

    if all_problematic_data:
        try:
            with open(args.output_json, 'w', encoding='utf-8') as f_out:
                json.dump(all_problematic_data, f_out,
                          indent=2, ensure_ascii=False)
            print(
                f"\nDados problemáticos extraídos e salvos em: {args.output_json}")
        except Exception as e:
            print(
                f"\nErro ao salvar o arquivo JSON em '{args.output_json}': {e}")
    else:
        print("\nNenhum dado problemático foi extraído para salvar no JSON.")

    print("\nProcessamento concluído.")


if __name__ == "__main__":
    main()

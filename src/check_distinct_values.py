#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ----------------------------------------------------------------------------
# Script: show_unique_values.py
# Autor: Seu Nome/Empresa
# Data: DD/MM/AAAA
# Versão: 1.0
# Licença: (Se aplicável)
# Descrição: Este script percorre um diretório de arquivos de dados (CSVs),
#            coleta e exibe os valores distintos para um conjunto de
#            colunas pré-definidas pelo usuário.
# ----------------------------------------------------------------------------

import os
import argparse
import sys
import pandas as pd
from utils import find_files, read_csv_robust


def main():
    parser = argparse.ArgumentParser(
        description="Mostra os valores distintos para colunas específicas em múltiplos arquivos de dados.",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument(
        "-d", "--root-directory", type=str, required=True,
        help="Diretório raiz onde os arquivos de dados originais estão localizados."
    )
    parser.add_argument(
        "-c", "--columns", nargs='+', required=True, type=str,
        help="Nomes das colunas a serem analisadas."
    )
    parser.add_argument(
        "-e", "--extensions", nargs='+', default=['csv'], type=str,
        help="Extensões a serem processadas. Padrão: csv"
    )
    parser.add_argument(
        "-r", "--recursive", action="store_true", default=True,
        help="Incluir subdiretórios na busca (padrão)."
    )
    parser.add_argument(
        "--no-recursive", action="store_false", dest="recursive",
        help="Não incluir subdiretórios na busca."
    )
    parser.add_argument(
        "--delimiter", type=str, default=";",
        help="Delimitador para arquivos CSV. Padrão: ';'"
    )

    args = parser.parse_args()

    root_dir = os.path.abspath(args.root_directory)
    if not os.path.isdir(root_dir):
        print(
            f"Erro: O diretório raiz '{root_dir}' não existe.", file=sys.stderr)
        sys.exit(1)

    actual_delimiter = args.delimiter.replace('\t', '\t')
    columns_to_analyze = args.columns

    # --- Início do Processamento ---
    files_to_process = find_files(
        root_dir, args.extensions, args.recursive)
    if not files_to_process:
        print("Nenhum arquivo encontrado com os critérios especificados.")
        return

    print(
        f"Encontrados {len(files_to_process)} arquivos. Analisando as colunas: {', '.join(columns_to_analyze)}\n")

    # Usamos um dicionário onde cada chave é um nome de coluna e o valor é um set.
    # Sets são ideais para coletar valores únicos de forma eficiente.
    unique_values_by_column = {col: set() for col in columns_to_analyze}

    for file_path in files_to_process:
        relative_path = os.path.relpath(file_path, root_dir)
        print(f"Processando arquivo: {relative_path}")

        try:
            # Lemos o arquivo, garantindo que colunas de interesse sejam tratadas como texto
            df = read_csv_robust(file_path, delimiter=actual_delimiter)
            if df is None:
                continue

            for col_name in columns_to_analyze:
                # Verifica se a coluna realmente existe no arquivo atual
                if col_name in df.columns:
                    # Coleta os valores únicos da coluna, removendo nulos (NaN) e os adiciona ao nosso set.
                    # .dropna() remove valores ausentes, .unique() obtém os distintos.
                    unique_in_file = df[col_name].dropna().unique()
                    unique_values_by_column[col_name].update(unique_in_file)
                else:
                    print(
                        f"  -> Aviso: Coluna '{col_name}' não encontrada em '{relative_path}'.")

        except ValueError as ve:
            # Este erro é comum se usecols não encontrar nenhuma coluna
            if "Columns not found" in str(ve):
                print(
                    f"  -> Aviso: Nenhuma das colunas alvo foi encontrada em '{relative_path}'.")
            else:
                print(
                    f"  ERRO ao ler o arquivo {relative_path}: {ve}", file=sys.stderr)
        except Exception as e:
            print(
                f"  ERRO ao processar o arquivo {relative_path}: {e}", file=sys.stderr)


    # --- Exibição dos Resultados ---
    print("\n\n" + "="*80)
    print("=== RESULTADO DA ANÁLISE DE VALORES DISTINTOS ===")
    print("="*80 + "\n")

    for col_name, unique_set in unique_values_by_column.items():
        print(f"--- Coluna: '{col_name}' ---")

        if not unique_set:
            print("Nenhum valor encontrado para esta coluna nos arquivos processados.\n")
            continue

        # Ordena os valores para uma exibição consistente e legível
        sorted_values = sorted(list(unique_set))

        print(
            f"Total de valores distintos encontrados: {len(sorted_values)}\n")

        for value in sorted_values:
            print(f"- {value}")

        print("\n" + "-"*50 + "\n")

    print("Análise concluída.")


if __name__ == "__main__":
    main()

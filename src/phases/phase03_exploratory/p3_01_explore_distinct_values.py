# -*- coding: utf-8 -*-

# --------------------------------------------------------------------------------
# Descrição: Este script percorre um diretório de arquivos de dados (CSVs),
#            coleta e exibe os valores distintos para um conjunto de
#            colunas pré-definidas pelo usuário.
# Exemplo de uso: python p3_01_explore_distinct_values.py --argumento valor
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
from src.utils import find_files, read_csv_robust


def explore_distinct_values(root_directory, columns, extensions, recursive, delimiter):
    """
    Percorre um diretório de arquivos de dados, coleta e exibe os valores distintos
    para um conjunto de colunas pré-definidas.
    """
    root_dir = os.path.abspath(root_directory)
    if not os.path.isdir(root_dir):
        print(f"Erro: O diretório raiz '{root_dir}' não existe.", file=sys.stderr)
        sys.exit(1)

    actual_delimiter = delimiter.replace('\t', '\t')
    columns_to_analyze = columns

    # --- Início do Processamento ---
    files_to_process = find_files(root_dir, extensions, recursive)
    if not files_to_process:
        print("Nenhum arquivo encontrado com os critérios especificados.")
        return

    print(
        f"Encontrados {len(files_to_process)} arquivos. Analisando as colunas: {', '.join(columns_to_analyze)}\n")

    unique_values_by_column = {col: set() for col in columns_to_analyze}

    for file_path in files_to_process:
        relative_path = os.path.relpath(file_path, root_dir)
        print(f"Processando arquivo: {relative_path}")

        try:
            df = read_csv_robust(file_path, delimiter=actual_delimiter)
            if df is None:
                continue

            for col_name in columns_to_analyze:
                if col_name in df.columns:
                    unique_in_file = df[col_name].dropna().unique()
                    unique_values_by_column[col_name].update(unique_in_file)
                else:
                    print(
                        f"  -> Aviso: Coluna '{col_name}' não encontrada em '{relative_path}'.")

        except ValueError as ve:
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

        sorted_values = sorted(list(unique_set))

        print(
            f"Total de valores distintos encontrados: {len(sorted_values)}\n")

        for value in sorted_values:
            print(f"- {value}")

        print("\n" + "-"*50 + "\n")

    print("Análise concluída.")


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

    explore_distinct_values(
        root_directory=args.root_directory,
        columns=args.columns,
        extensions=args.extensions,
        recursive=args.recursive,
        delimiter=args.delimiter
    )


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ----------------------------------------------------------------------------
# Script: generate_profiles.py
# Autor: Seu Nome/Empresa
# Data: DD/MM/AAAA
# Versão: 1.0
# Descrição: Gera relatórios de perfilamento de dados com ydata-profiling
#            para múltiplos arquivos e os salva como arquivos HTML individuais.
# ----------------------------------------------------------------------------

import os
import argparse
import sys
import pandas as pd
from ydata_profiling import ProfileReport
from utils import find_files, read_csv_robust


def main():
    parser = argparse.ArgumentParser(
        description="Gera relatórios HTML de perfilamento de dados para múltiplos arquivos.",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument(
        "-d", "--root-directory", type=str, required=True,
        help="Diretório raiz onde os arquivos de dados estão localizados."
    )
    parser.add_argument(
        "-o", "--output-directory", type=str, required=True,
        help="Diretório de saída para salvar os relatórios HTML."
    )
    parser.add_argument(
        "-e", "--extensions", nargs='+', default=['csv', 'xlsx', 'xls', 'json'], type=str,
        help="Extensões a serem consideradas. Padrão: csv xlsx xls json"
    )
    parser.add_argument(
        "-r", "--recursive", action="store_true", help="Incluir subdiretórios na busca."
    )
    parser.add_argument(
        "--delimiter", type=str, default=",", help="Delimitador para arquivos CSV. Padrão: ','"
    )

    args = parser.parse_args()

    # Validação de diretórios
    root_dir = os.path.abspath(args.root_directory)
    output_dir = os.path.abspath(args.output_directory)
    os.makedirs(output_dir, exist_ok=True)

    if root_dir == output_dir:
        print(
            "Erro: Diretório de entrada e saída não podem ser os mesmos.", file=sys.stderr)
        sys.exit(1)

    files_to_profile = find_files(
        root_dir, args.extensions, args.recursive)
    if not files_to_profile:
        print("Nenhum arquivo encontrado.")
        return

    print(
        f"Encontrados {len(files_to_profile)} arquivos. Gerando relatórios...")

    for file_path in files_to_profile:
        filename = os.path.basename(file_path)
        print(f"  -> Processando: {filename}")

        try:
            df = None
            if file_path.lower().endswith('.csv'):
                df = read_csv_robust(file_path, delimiter=args.delimiter.replace('\t', '\t'))
            elif file_path.lower().endswith(('.xlsx', '.xls')):
                # Para simplificar, vamos gerar um relatório apenas para a primeira planilha
                df = pd.read_excel(file_path, sheet_name=0)
            elif file_path.lower().endswith('.json'):
                df = pd.read_json(file_path)

            if df is not None:
                profile = ProfileReport(
                    df, title=f"Relatório de Análise para {filename}")

                output_filename = f"{os.path.splitext(filename)[0]}_profile.html"
                output_path = os.path.join(output_dir, output_filename)

                profile.to_file(output_path)
                print(f"     Relatório salvo em: {output_path}")

        except Exception as e:
            print(f"     ERRO ao processar {filename}: {e}", file=sys.stderr)


    print("\nProcesso concluído.")


if __name__ == "__main__":
    main()

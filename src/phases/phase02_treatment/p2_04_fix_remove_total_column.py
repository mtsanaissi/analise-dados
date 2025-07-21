# -*- coding: utf-8 -*-

# --------------------------------------------------------------------------------
# Descrição: Este script processa arquivos CSV em um diretório especificado
#            e, opcionalmente, em seus subdiretórios.
#            Para cada arquivo CSV, ele verifica se a última coluna se chama
#            "Total" (ignorando maiúsculas/minúsculas e espaços extras).
#            Se for o caso, remove essa coluna e salva o arquivo CSV
#            modificado, substituindo o original ou salvando com novo nome.
# Exemplo de uso: python p2_04_fix_remove_total_column.py --argumento valor
#
# Autor: Marcelo Anaissi
# Criado em: 29/05/2025
# Versão: 1.2
#
# Modificado por: Jules
# Modificado em: 21/07/2025
# Licença: MIT
# --------------------------------------------------------------------------------

import os
import argparse
import pandas as pd
import sys
import csv  # Para a constante de quoting
from utils import find_files, read_csv_robust, save_df_to_csv

# Constante para o nome da coluna a ser removida
COLUMN_TO_REMOVE_NAME = "total"


def process_csv_file(file_path, overwrite_original=True, output_suffix="_fixed"):
    """
    Processa um único arquivo CSV para remover a coluna "Total", se existir como última coluna.

    Args:
        file_path (str): Caminho completo para o arquivo CSV.
        overwrite_original (bool): Se True, substitui o arquivo original.
                                   Se False, salva com um sufixo.
        output_suffix (str): Sufixo a ser adicionado ao nome do arquivo se não for sobrescrever.

    Returns:
        bool: True se o processamento foi bem-sucedido (ou se a coluna não precisou ser removida),
              False se ocorreu um erro.
    """
    print(f"\nProcessando arquivo: {file_path}")
    try:
        encodings_to_try = ['utf-8', 'latin-1', 'iso-8859-1', 'cp1252']
        df = None
        detected_encoding = None

        for enc in encodings_to_try:
            try:
                df = pd.read_csv(file_path, encoding=enc, delimiter=";",
                                 dtype=str, keep_default_na=False)
                detected_encoding = enc
                print(
                    f"  Arquivo lido com sucesso usando encoding: {detected_encoding}")
                break
            except UnicodeDecodeError:
                # print(f"  Falha ao ler com encoding {enc}...") # Opcional, pode poluir o log
                pass
            except Exception as e_read:
                print(
                    f"  Erro inesperado ao tentar ler o arquivo com encoding {enc}: {e_read}")
                return False

        if df is None:
            print(
                f"  Erro: Não foi possível ler o arquivo CSV '{os.path.basename(file_path)}' com os encodings testados.")
            return False

        if df.empty:
            print("  Aviso: O arquivo CSV está vazio. Nenhuma alteração será feita.")
            return True

        if not df.columns.any():
            print(
                "  Aviso: O arquivo CSV não possui cabeçalho ou colunas. Nenhuma alteração será feita.")
            return True

        last_column_name_original = df.columns[-1]
        normalized_last_column_name = str(
            last_column_name_original).strip().lower()

        if normalized_last_column_name == COLUMN_TO_REMOVE_NAME:
            print(
                f"  Coluna '{last_column_name_original}' encontrada como última coluna. Removendo...")
            df_modified = df.drop(columns=[last_column_name_original])

            if overwrite_original:
                output_path = file_path
                print(
                    f"  Salvando arquivo modificado (sobrescrevendo): {output_path}")
            else:
                base, ext = os.path.splitext(file_path)
                output_path = f"{base}{output_suffix}{ext}"
                print(f"  Salvando arquivo modificado em: {output_path}")

            df_modified.to_csv(
                output_path, index=False, encoding=detected_encoding, quoting=csv.QUOTE_MINIMAL)
            print(f"  Arquivo salvo com sucesso.")
        else:
            print(
                f"  A última coluna ('{last_column_name_original}') não é '{COLUMN_TO_REMOVE_NAME.capitalize()}'. Nenhuma alteração feita.")

        return True

    except pd.errors.EmptyDataError:
        print("  Aviso: O arquivo CSV está vazio (detectado pelo Pandas). Nenhuma alteração será feita.")
        return True
    except Exception as e:
        print(f"  Erro inesperado ao processar o arquivo: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(
        description="Remove a última coluna chamada 'Total' de arquivos CSV em um diretório (e opcionalmente subdiretórios).",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument(
        "input_directory",
        type=str,
        help="Diretório raiz contendo os arquivos CSV a serem processados.\nExemplo: ../data/fix/ ou ./csv_para_corrigir"
    )
    parser.add_argument(
        "-r", "--recursive",
        action="store_true",
        help="Incluir subdiretórios na busca por arquivos CSV."
    )
    parser.add_argument(
        "--no-overwrite",
        action="store_false",
        dest="overwrite_original",
        default=True,
        help="Não sobrescrever os arquivos originais. Em vez disso, salva os arquivos modificados\ncom o sufixo especificado (padrão: '_fixed')."
    )
    parser.add_argument(
        "--suffix",
        type=str,
        default="_fixed",
        help="Sufixo a ser usado para arquivos modificados se --no-overwrite estiver ativo.\nPadrão: _fixed"
    )

    args = parser.parse_args()

    try:
        target_directory = os.path.abspath(
            os.path.expanduser(args.input_directory))
    except Exception as e:
        print(
            f"Erro Crítico: Falha ao processar o caminho do diretório de entrada '{args.input_directory}': {e}")
        sys.exit(1)

    print(f"--- Configuração do Processamento ---")
    print(f"Diretório de Entrada: {target_directory}")
    print(f"Buscar Recursivamente: {'Sim' if args.recursive else 'Não'}")
    print(
        f"Sobrescrever Arquivos Originais: {'Sim' if args.overwrite_original else 'Não'}")
    if not args.overwrite_original:
        print(f"Sufixo para Novos Arquivos: {args.suffix}")
    print(
        f"Coluna a ser Removida (se for a última): '{COLUMN_TO_REMOVE_NAME.capitalize()}'")
    print(f"-----------------------------------\n")

    csv_files_to_process = find_csv_files_recursive(
        target_directory, args.recursive)

    if not csv_files_to_process:
        print(
            f"Nenhum arquivo CSV encontrado com os critérios especificados em '{target_directory}'.")
        sys.exit(0)

    print(
        f"Encontrados {len(csv_files_to_process)} arquivo(s) CSV para processar.\n")

    successful_processing_count = 0
    failed_processing_count = 0

    for csv_file in csv_files_to_process:
        if process_csv_file(csv_file, args.overwrite_original, args.suffix):
            successful_processing_count += 1
        else:
            failed_processing_count += 1

    print("\n--- Resumo do Processamento ---")
    print(f"Total de arquivos CSV encontrados: {len(csv_files_to_process)}")
    print(
        f"Arquivos processados com sucesso (ou sem necessidade de alteração): {successful_processing_count}")
    print(f"Arquivos que falharam no processamento: {failed_processing_count}")

    if failed_processing_count > 0:
        print("\nPor favor, revise os logs de erro para os arquivos que falharam.")

    print("\nProcessamento concluído.")


if __name__ == "__main__":
    main()

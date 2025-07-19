#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ----------------------------------------------------------------------------
# Script: convert_delimiter.py
# Autor: Seu Nome/Empresa
# Data: DD/MM/AAAA
# Versão: 1.0
# Licença: (Se aplicável)
# Descrição: Este script converte o delimitador de arquivos CSV de um
#            diretório de origem para um diretório de destino,
#            preservando a estrutura de pastas.
# ----------------------------------------------------------------------------

import os
import argparse
import sys
import pandas as pd
from ..utils import find_files, read_csv_robust, save_df_to_csv


def main():
    parser = argparse.ArgumentParser(
        description="Converte o delimitador de arquivos CSV.",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument(
        "-d", "--source-directory",
        type=str,
        required=True,
        help="Diretório de origem contendo os arquivos CSV a serem convertidos."
    )
    parser.add_argument(
        "-o", "--output-directory",
        type=str,
        required=True,
        help="Diretório de destino para salvar os arquivos convertidos.\nEste diretório será criado se não existir. NÃO PODE ser o mesmo que o de origem."
    )
    parser.add_argument(
        "--from-delimiter",
        type=str,
        default=";",
        help="O delimitador ATUAL dos arquivos de origem.\nPadrão: ';' (ponto e vírgula). Use '\t' para TAB."
    )
    parser.add_argument(
        "--to-delimiter",
        type=str,
        default=",",
        help="O NOVO delimitador para os arquivos de destino.\nPadrão: ',' (vírgula). Use '\t' para TAB."
    )
    parser.add_argument(
        "-r", "--recursive",
        action="store_true",
        help="Processar arquivos em subdiretórios recursivamente. Padrão: não processar."
    )

    args = parser.parse_args()

    # --- Validações e Preparação ---
    source_dir_abs = os.path.abspath(os.path.expanduser(args.source_directory))
    output_dir_abs = os.path.abspath(os.path.expanduser(args.output_directory))

    if source_dir_abs == output_dir_abs:
        print("Erro Crítico: O diretório de origem e de destino não podem ser os mesmos.")
        print("Por favor, especifique um diretório de saída diferente para evitar sobrescrever dados.")
        sys.exit(1)

    from_delimiter = args.from_delimiter.replace('\t', '\t')
    to_delimiter = args.to_delimiter.replace('\t', '\t')

    if from_delimiter == to_delimiter:
        print("Aviso: O delimitador de origem e de destino são idênticos. Nenhuma conversão será realizada.")
        sys.exit(0)

    print("--- Configurações da Conversão de Delimitador ---")
    print(f"Diretório de Origem: {source_dir_abs}")
    print(f"Diretório de Destino: {output_dir_abs}")
    print(f"Delimitador de Origem: '{from_delimiter}'")
    print(f"Novo Delimitador: '{to_delimiter}'")
    print(f"Processar Subdiretórios: {'Sim' if args.recursive else 'Não'}")
    print("--------------------------------------------------\n")

    discovered_files = find_files(source_dir_abs, ['csv'], args.recursive)

    if not discovered_files:
        print("Nenhum arquivo CSV encontrado no diretório de origem especificado.")
        sys.exit(0)

    print(
        f"Encontrados {len(discovered_files)} arquivo(s) CSV. Iniciando conversão...\n")

    success_count = 0
    error_count = 0

    # --- Loop de Conversão ---
    for source_file_path in discovered_files:
        relative_path = os.path.relpath(source_file_path, source_dir_abs)
        print(f"Processando: {relative_path} ...")

        try:
            # Constrói o caminho de saída preservando a estrutura de subdiretórios
            output_file_path = os.path.join(output_dir_abs, relative_path)

            # Lê o arquivo CSV de forma robusta com o delimitador de origem
            df = read_csv_robust(source_file_path, delimiter=from_delimiter)

            if df is None:
                # O erro já foi impresso pela função read_csv_robust
                error_count += 1
                continue
            
            if df.empty:
                print("  -> Aviso: Arquivo de origem vazio ou sem dados. Gerando arquivo de destino vazio.")

            # Salva o DataFrame com o novo delimitador usando a função utilitária
            if save_df_to_csv(df, output_file_path, delimiter=to_delimiter):
                print(f"  -> Salvo em: {output_file_path}")
                success_count += 1
            else:
                # O erro já foi impresso pela função save_df_to_csv
                error_count += 1

        except Exception as e:
            print(f"  ERRO Inesperado ao processar '{relative_path}': {e}")
            error_count += 1

    # --- Resumo Final ---
    print("\n--- Resumo da Conversão ---")
    print(f"Arquivos processados com sucesso: {success_count}")
    print(f"Arquivos que falharam: {error_count}")
    print("---------------------------\n")

    if error_count > 0:
        print("Dica: Se ocorreram erros de parsing, use o script 'detect_delimiter.py' para verificar se o delimitador de origem está correto para os arquivos que falharam.")

    print("Conversão de delimitadores concluída.")


if __name__ == "__main__":
    main()
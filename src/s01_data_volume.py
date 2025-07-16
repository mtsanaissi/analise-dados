#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ----------------------------------------------------------------------------
# Script: summarize_data_volume.py
# Autor: Seu Nome/Empresa
# Data: DD/MM/AAAA
# Versão: 1.0
# Licença: (Se aplicável)
# Descrição: Este script analisa o volume de dados em um diretório,
#            calculando a contagem de registros e o tamanho em disco
#            para arquivos CSV, Excel e JSON. Apresenta um resumo
#            agregado por tipo de arquivo.
# ----------------------------------------------------------------------------

import os
import argparse
import sys
import pandas as pd
import json
from utils import find_files


def get_file_metrics(file_path, delimiter):
    """
    Obtém métricas (registros e tamanho) para um único arquivo, despachando para a função correta.
    """
    _, file_ext_with_dot = os.path.splitext(file_path)
    extension = file_ext_with_dot.lstrip('.').lower()

    file_size = os.path.getsize(file_path)
    record_count = 0
    error_message = None

    try:
        if extension == 'csv':
            # Para CSV, o número de linhas é uma boa aproximação de registros.
            # O Pandas lida corretamente com cabeçalhos.
            # Para arquivos muito grandes, ler em chunks seria mais eficiente, mas isso é mais robusto.
            df = pd.read_csv(file_path, sep=delimiter)
            record_count = len(df)
        elif extension in ['xlsx', 'xls']:
            # Para Excel, somamos os registros de todas as planilhas.
            xls = pd.ExcelFile(file_path)
            for sheet_name in xls.sheet_names:
                df = pd.read_excel(xls, sheet_name=sheet_name)
                record_count += len(df)
        elif extension == 'json':
            # Para JSON, a definição de "registro" depende da estrutura.
            # Tenta primeiro como um JSON padrão (lista de objetos ou objeto único).
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        record_count = len(data)
                    elif isinstance(data, dict):
                        record_count = 1  # Um único objeto JSON
            except (json.JSONDecodeError, TypeError):
                # Se falhar, tenta como JSON Lines, que é comum para grandes datasets.
                try:
                    df = pd.read_json(file_path, lines=True)
                    record_count = len(df)
                except (ValueError, TypeError):
                    # Se ambos falharem, o erro será capturado abaixo.
                    raise ValueError("Formato JSON não suportado (nem padrão, nem Lines).")

    except pd.errors.EmptyDataError:
        record_count = 0  # Arquivo vazio, sem erro
    except Exception as e:
        error_message = str(e)
        record_count = 0

    return {
        "arquivo": file_path,
        "extensao": extension,
        "registros": record_count,
        "tamanho_bytes": file_size,
        "erro": error_message
    }


def format_bytes(size_bytes):
    """
    Formata um tamanho em bytes para uma unidade mais legível (KB, MB, GB).
    """
    if size_bytes is None:
        return "N/A"
    if size_bytes < 1024:
        return f"{size_bytes} B"
    if size_bytes < 1024**2:
        return f"{size_bytes/1024:.2f} KB"
    if size_bytes < 1024**3:
        return f"{size_bytes/1024**2:.2f} MB"
    return f"{size_bytes/1024**3:.2f} GB"


def main():
    parser = argparse.ArgumentParser(
        description="Gera um resumo do volume e tamanho de arquivos de dados.",
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
        default=['csv', 'xlsx', 'xls', 'json'],
        type=str,
        help="Lista de extensões de arquivo a serem consideradas.\nPadrão: csv xlsx xls json"
    )
    parser.add_argument(
        "-r", "--recursive",
        action="store_true",
        help="Incluir subdiretórios na busca. Padrão: não incluir."
    )
    parser.add_argument(
        "--delimiter",
        type=str,
        default=";",
        help="Delimitador para arquivos CSV.\nPadrão: ',' (vírgula). Use '\\t' para TAB."
    )
    parser.add_argument(
        "-o", "--output-report",
        type=str,
        help="Caminho opcional para salvar o relatório agregado em formato CSV."
    )

    args = parser.parse_args()

    # Trata o delimitador TAB
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

    print("--- Configurações do Resumo de Volume ---")
    print(f"Diretório Raiz: {root_dir_processed}")
    print(f"Extensões Alvo: {', '.join(args.extensions)}")
    print(f"Buscar em Subdiretórios: {'Sim' if args.recursive else 'Não'}")
    if 'csv' in args.extensions:
        print(f"Delimitador CSV: '{actual_delimiter}'")
    print("-----------------------------------------\n")

    discovered_files = find_files(
        root_dir_processed, args.extensions, args.recursive)

    if not discovered_files:
        print("Nenhum arquivo encontrado com os critérios especificados.")
        sys.exit(0)

    print(
        f"Encontrados {len(discovered_files)} arquivo(s). Coletando métricas...")

    all_metrics = [get_file_metrics(f, actual_delimiter)
                   for f in discovered_files]

    # Filtra arquivos que tiveram erro de leitura de métricas para não poluir o resumo
    files_with_errors = [m for m in all_metrics if m['erro']]
    valid_metrics = [m for m in all_metrics if not m['erro']]

    if not valid_metrics:
        print("\nNenhum arquivo pôde ser lido com sucesso para gerar o resumo.")
        if files_with_errors:
            print("Arquivos com erro:")
            for m in files_with_errors:
                print(f"  - {os.path.basename(m['arquivo'])}: {m['erro']}")
        sys.exit(0)

    # Cria um DataFrame para facilitar a agregação
    df_metrics = pd.DataFrame(valid_metrics)

    # Agrega os dados por extensão
    summary = df_metrics.groupby('extensao').agg(
        total_arquivos=('arquivo', 'count'),
        total_registros=('registros', 'sum'),
        total_tamanho_bytes=('tamanho_bytes', 'sum')
    ).reset_index()

    # Calcula médias
    summary['media_registros_por_arquivo'] = summary['total_registros'] / \
        summary['total_arquivos']
    summary['media_tamanho_por_arquivo'] = summary['total_tamanho_bytes'] / \
        summary['total_arquivos']

    print("\n--- Resumo de Volume e Tamanho por Extensão ---\n")

    # Imprime o cabeçalho da tabela
    header = (f"{'Extensão':<10} | {'Total Arquivos':>15} | {'Total Registros':>18} | {'Tamanho Total':>15} | "
              f"{'Média Registros/Arq':>20} | {'Média Tamanho/Arq':>20}")
    print(header)
    print("-" * len(header))

    # Imprime os dados da tabela
    for _, row in summary.iterrows():
        print(f"{row['extensao']:<10} | "
              f"{row['total_arquivos']:>15,d} | "
              f"{row['total_registros']:>18,d} | "
              f"{format_bytes(row['total_tamanho_bytes']):>15} | "
              f"{row['media_registros_por_arquivo']:>20,.2f} | "
              f"{format_bytes(row['media_tamanho_por_arquivo']):>20}")

    # Imprime o total geral
    print("-" * len(header))
    total_arquivos_geral = summary['total_arquivos'].sum()
    total_registros_geral = summary['total_registros'].sum()
    total_tamanho_geral = summary['total_tamanho_bytes'].sum()
    print(f"{'TOTAL GERAL':<10} | "
          f"{total_arquivos_geral:>15,d} | "
          f"{total_registros_geral:>18,d} | "
          f"{format_bytes(total_tamanho_geral):>15} | "
          f"{'':>20} | {'':>20}")

    if files_with_errors:
        print("\n--- Arquivos com Erros de Leitura (ignorados no resumo) ---")
        for m in files_with_errors:
            print(f"  - {os.path.basename(m['arquivo'])}: {m['erro']}")

    if args.output_report:
        try:
            summary.to_csv(args.output_report, index=False,
                           encoding='utf-8-sig')
            print(
                f"\nRelatório agregado salvo com sucesso em: {args.output_report}")
        except Exception as e:
            print(
                f"\nErro ao salvar o relatório em '{args.output_report}': {e}")

    print("\nResumo concluído.")


if __name__ == "__main__":
    main()

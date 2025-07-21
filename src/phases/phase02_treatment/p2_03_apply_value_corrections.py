# -*- coding: utf-8 -*-

# --------------------------------------------------------------------------------
# Descrição: Este script aplica correções a arquivos CSV com base em um
#            mapa de correções e uma lista de tarefas (arquivos e colunas
#            problemáticos). Os arquivos corrigidos são salvos em um
#            diretório de saída especificado.
# Exemplo de uso: python p2_03_apply_value_corrections.py --argumento valor
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
import json
from ..utils import read_csv_robust, save_df_to_csv


def apply_csv_corrections(
    root_dir,
    output_dir,
    tasks_file_path,
    corrections_map_path,
    csv_delimiter
):
    """
    Aplica correções a arquivos CSV com base nos arquivos JSON de entrada.

    Args:
        root_dir (str): O diretório raiz onde os CSVs originais estão.
        output_dir (str): O diretório onde os CSVs corrigidos serão salvos.
        tasks_file_path (str): Caminho para o JSON com a lista de tarefas.
        corrections_map_path (str): Caminho para o JSON com o mapa de correções.
        csv_delimiter (str): O delimitador usado nos arquivos CSV.
    """
    # --- 1. Carregar os arquivos JSON ---
    try:
        print(f"Carregando a lista de tarefas de: {tasks_file_path}")
        with open(tasks_file_path, 'r', encoding='utf-8') as f:
            tasks = json.load(f)
    except FileNotFoundError:
        print(
            f"Erro Crítico: O arquivo de tarefas '{tasks_file_path}' não foi encontrado.")
        sys.exit(1)
    except json.JSONDecodeError:
        print(
            f"Erro Crítico: O arquivo de tarefas '{tasks_file_path}' não é um JSON válido.")
        sys.exit(1)

    try:
        print(f"Carregando o mapa de correções de: {corrections_map_path}")
        with open(corrections_map_path, 'r', encoding='utf-8') as f:
            corrections_map = json.load(f)
    except FileNotFoundError:
        print(
            f"Erro Crítico: O arquivo de mapa de correções '{corrections_map_path}' não foi encontrado.")
        sys.exit(1)
    except json.JSONDecodeError:
        print(
            f"Erro Crítico: O arquivo de mapa de correções '{corrections_map_path}' não é um JSON válido.")
        sys.exit(1)

    print(
        f"\nIniciando processo de correção para {len(tasks)} tarefa(s) de arquivo...\n")
    files_corrected_count = 0
    files_with_errors_count = 0

    # --- 2. Iterar sobre as tarefas ---
    for task in tasks:
        if 'arquivo' not in task:
            print(
                "  Aviso: Encontrada uma entrada na lista de tarefas sem a chave 'arquivo'. Pulando.")
            continue

        relative_file_path = task['arquivo']
        original_file_path = os.path.join(root_dir, relative_file_path)

        print(f"Processando tarefa para o arquivo: {relative_file_path}")

        if not os.path.exists(original_file_path):
            print(
                f"  Erro: Arquivo original não encontrado em '{original_file_path}'. Pulando.")
            files_with_errors_count += 1
            continue

        # --- 3. Ler o CSV e aplicar correções ---
        try:
            df = read_csv_robust(original_file_path, delimiter=csv_delimiter)
            if df is None:
                files_with_errors_count += 1
                continue

            # Itera sobre as colunas listadas na tarefa (ignorando a chave 'arquivo')
            for column_name in task:
                if column_name == 'arquivo':
                    continue

                if column_name in df.columns:
                    print(
                        f"  -> Aplicando correções na coluna: '{column_name}'")
                    # O método .replace() usa o dicionário para fazer todas as substituições de uma vez.
                    # É eficiente e lida com valores que não estão no dicionário (simplesmente os ignora).
                    df[column_name] = df[column_name].replace(corrections_map)
                else:
                    print(
                        f"  Aviso: A coluna '{column_name}' foi listada como problemática, mas não foi encontrada no arquivo.")

            # --- 4. Salvar o arquivo corrigido ---
            output_file_path = os.path.join(output_dir, relative_file_path)

            if save_df_to_csv(df, output_file_path, delimiter=csv_delimiter):
                print(f"  -> Arquivo corrigido salvo em: {output_file_path}")
                files_corrected_count += 1
            else:
                files_with_errors_count += 1

        except Exception as e:
            print(
                f"  Erro inesperado ao processar ou salvar o arquivo '{original_file_path}': {e}")
            files_with_errors_count += 1

    print("\n--- Resumo da Correção ---")
    print(f"Total de tarefas de arquivo processadas: {len(tasks)}")
    print(f"Arquivos corrigidos e salvos com sucesso: {files_corrected_count}")
    print(
        f"Arquivos que falharam durante o processo: {files_with_errors_count}")


def main():
    parser = argparse.ArgumentParser(
        description="Aplica correções a arquivos CSV usando um mapa de substituição.",
        formatter_class=argparse.RawTextHelpFormatter
    )

    parser.add_argument(
        "-d", "--root-directory",
        type=str,
        required=True,
        help="Diretório raiz onde os arquivos CSV originais estão localizados."
    )
    parser.add_argument(
        "-o", "--output-directory",
        type=str,
        required=True,
        help="Diretório de saída para salvar os arquivos CSV corrigidos.\nSerá criado se não existir. NÃO DEVE SER O MESMO DIRETÓRIO RAIZ."
    )
    parser.add_argument(
        "-t", "--tasks-file",
        type=str,
        default="04b_problematic_csv_values.json",
        help="Caminho para o arquivo JSON contendo a lista de tarefas (arquivos e colunas a serem corrigidos).\nPadrão: problematic_csv_values.json"
    )
    parser.add_argument(
        "-m", "--map-file",
        type=str,
        default="04c_corrections_map.json",
        help="Caminho para o arquivo JSON contendo o mapa de correções (de-para).\nPadrão: corrections_map.json"
    )
    parser.add_argument(
        "--delimiter",
        type=str,
        default=";",
        help="Delimitador utilizado nos arquivos CSV.\nPadrão: ';' (ponto e vírgula).\nUse '\t' para TAB."
    )

    args = parser.parse_args()

    # Validação crítica para evitar sobrescrever os dados originais
    root_dir_processed = os.path.abspath(
        os.path.expanduser(args.root_directory))
    output_dir_processed = os.path.abspath(
        os.path.expanduser(args.output_directory))

    if root_dir_processed == output_dir_processed:
        print(
            "Erro Crítico: O diretório de saída não pode ser o mesmo que o diretório raiz.")
        print("Por favor, especifique um diretório de saída diferente para evitar a perda de dados originais.")
        sys.exit(1)

    # Trata o delimitador TAB
    actual_delimiter = args.delimiter
    if actual_delimiter == '\t':
        actual_delimiter = '\t'

    print("--- Configurações da Aplicação de Correções ---")
    print(f"Diretório Raiz dos Originais: {root_dir_processed}")
    print(f"Diretório de Saída dos Corrigidos: {output_dir_processed}")
    print(f"Arquivo de Tarefas: {args.tasks_file}")
    print(f"Arquivo de Mapa de Correções: {args.map_file}")
    print(f"Delimitador CSV: '{actual_delimiter}'")
    print("----------------------------------------------\n")

    apply_csv_corrections(
        root_dir_processed,
        output_dir_processed,
        args.tasks_file,
        args.map_file,
        actual_delimiter
    )

    print("\nProcesso de correção concluído.")


if __name__ == "__main__":
    main()

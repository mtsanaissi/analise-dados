#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ----------------------------------------------------------------------------
# Script: filter_data_batch.py
# Autor: Seu Nome/Empresa
# Data: DD/MM/AAAA
# Versão: 1.2 (Atualizado filtro de segmentos e corrigida a lógica de busca de arquivos)
# Licença: (Se aplicável)
# Descrição: Este script processa arquivos de dados em lote. Ele lê
#            arquivos de um diretório raiz, aplica um conjunto de filtros
#            personalizáveis e salva os dados filtrados em um diretório
#            de saída, preservando a estrutura de pastas original.
# ----------------------------------------------------------------------------

import os
import argparse
import sys
import pandas as pd

# --- Início da Lógica de Descoberta de Arquivos (Corrigida e Otimizada) ---


def find_data_files(root_path, target_extensions, search_recursively):
    """
    Encontra arquivos de dados em um diretório com base nas extensões fornecidas.
    A lógica foi corrigida para usar os métodos mais apropriados para busca
    recursiva e não recursiva.
    """
    found_files = []
    normalized_extensions = [ext.lower().lstrip('.')
                             for ext in target_extensions]
    if not os.path.isdir(root_path):
        return []

    if search_recursively:
        # Usa os.walk para a busca recursiva, que é o seu propósito.
        for dirpath, _, filenames in os.walk(root_path):
            for filename in filenames:
                # Extração robusta da extensão
                _, file_ext_with_dot = os.path.splitext(filename)
                file_extension = file_ext_with_dot.lstrip('.').lower()
                if file_extension in normalized_extensions:
                    found_files.append(os.path.join(dirpath, filename))
    else:
        # Usa os.listdir para a busca não recursiva, que é mais direto e correto.
        for filename in os.listdir(root_path):
            full_path = os.path.join(root_path, filename)
            # Garante que estamos processando um arquivo, não um subdiretório
            if os.path.isfile(full_path):
                _, file_ext_with_dot = os.path.splitext(filename)
                file_extension = file_ext_with_dot.lstrip('.').lower()
                if file_extension in normalized_extensions:
                    found_files.append(full_path)

    return found_files
# --- Fim da Lógica de Descoberta de Arquivos ---


# ============================================================================
# === INÍCIO DA SEÇÃO DE FILTROS EDITÁVEL PELO USUÁRIO ========================
# ============================================================================

def apply_user_filters(df):
    """
    Aplica todos os filtros definidos pelo usuário a um DataFrame.
    """
    print("  -> Aplicando filtros definidos pelo usuário...")

    df_filtered = df.copy()

    # --- ETAPA 1: Conversão de Tipos ---
    df_filtered.loc[:, 'Tempo Resposta'] = pd.to_numeric(
        df_filtered['Tempo Resposta'], errors='coerce')

    # --- ETAPA 2: Aplicação de Filtros ---

    # Filtro 1: Manter apenas as linhas onde 'Segmento de Mercado' está na lista ATUALIZADA.
    segmentos_desejados = [
        "Operadoras de Telecomunicações (Telefonia, Internet, TV por assinatura)",
        "Energia Elétrica",
        "Operadoras de Planos de Saúde e Administradoras de Benefícios",
        "Transporte Aéreo",
        "Transporte Terrestre"
    ]
    df_filtered = df_filtered[df_filtered['Segmento de Mercado'].isin(
        segmentos_desejados)]

    # Filtro 2: Manter apenas as linhas onde 'Tempo Resposta' é maior ou igual a 0.
    df_filtered = df_filtered[df_filtered['Tempo Resposta'] >= 0]

    return df_filtered

# ============================================================================
# === FIM DA SEÇÃO DE FILTROS EDITÁVEL PELO USUÁRIO ===========================
# ============================================================================


def filter_random_rows(df, num_rows):
    # Recebe um dataframe pandas e filtra registros aleatórios para retornar até
    # o número de linhas informado como parâmetro
    return df.sample(n=num_rows, random_state=42)


def main():
    parser = argparse.ArgumentParser(
        description="Filtra arquivos de dados em lote com base em regras personalizadas.",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument(
        "-d", "--root-directory", type=str, required=True,
        help="Diretório raiz onde os arquivos de dados originais estão localizados."
    )
    parser.add_argument(
        "-o", "--output-directory", type=str, required=True,
        help="Diretório de saída para salvar os arquivos filtrados."
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
    output_dir = os.path.abspath(args.output_directory)

    if not os.path.isdir(root_dir):
        print(
            f"Erro: O diretório raiz '{root_dir}' não existe.", file=sys.stderr)
        sys.exit(1)

    if root_dir == output_dir:
        print("Erro Crítico: O diretório de saída não pode ser o mesmo que o diretório raiz.", file=sys.stderr)
        sys.exit(1)

    os.makedirs(output_dir, exist_ok=True)
    actual_delimiter = args.delimiter.replace('\\t', '\t')

    files_to_process = find_data_files(
        root_dir, args.extensions, args.recursive)
    if not files_to_process:
        print("Nenhum arquivo encontrado com os critérios especificados.")
        return

    print(
        f"Encontrados {len(files_to_process)} arquivos. Iniciando filtragem...\n")
    processed_count = 0
    failed_count = 0

    for file_path in files_to_process:
        relative_path = os.path.relpath(file_path, root_dir)
        print(f"Processando: {relative_path}")

        try:
            df = pd.read_csv(file_path, sep=actual_delimiter, low_memory=False)
            original_row_count = len(df)

            if original_row_count == 0:
                print("  -> Arquivo vazio, pulando.")
                continue

            filtered_df = apply_user_filters(df)
            filtered_row_count = len(filtered_df)

            print(
                f"  -> {original_row_count:,} linhas originais -> {filtered_row_count:,} linhas filtradas.")

            output_file_path = os.path.join(output_dir, relative_path)
            output_file_dir = os.path.dirname(output_file_path)
            os.makedirs(output_file_dir, exist_ok=True)

            filtered_df.to_csv(
                output_file_path, sep=actual_delimiter, index=False, encoding='utf-8-sig')
            print(f"  -> Arquivo filtrado salvo em: {output_file_path}")
            processed_count += 1

        except FileNotFoundError:
            print(
                f"  ERRO: Arquivo não encontrado no caminho: {file_path}", file=sys.stderr)
            failed_count += 1
        except KeyError as e:
            print(
                f"  ERRO: Coluna não encontrada para o filtro: {e}. Verifique se a coluna existe em '{relative_path}'.", file=sys.stderr)
            failed_count += 1
        except Exception as e:
            print(
                f"  ERRO ao processar o arquivo {relative_path}: {e}", file=sys.stderr)
            failed_count += 1

        print("-" * 50)

    print("\nProcesso de filtragem concluído.")
    print(f"Total de arquivos processados com sucesso: {processed_count}")
    print(f"Total de arquivos com falha: {failed_count}")


if __name__ == "__main__":
    main()

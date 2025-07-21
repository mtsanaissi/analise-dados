# -*- coding: utf-8 -*-

# --------------------------------------------------------------------------------
# Descrição: Este script realiza um perfilamento (profiling) detalhado
#            de cada coluna em arquivos de dados (CSV, Excel, JSON).
#            Ele infere o tipo de dado e calcula estatísticas
#            descritivas, gerando um relatório estruturado em JSON.
# Exemplo de uso: python p1_06_profile_data_columns.py --argumento valor
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
import sys
import pandas as pd
import json
import numpy as np
from ..utils import find_files, read_csv_robust

# Não precisamos mais do 'warnings' se a lógica for melhorada


# Lista de formatos de data comuns para teste rápido
COMMON_DATE_FORMATS = [
    # Formatos mais comuns primeiro
    '%Y-%m-%d %H:%M:%S', '%d/%m/%Y %H:%M', '%Y-%m-%d', '%d/%m/%Y',
    # Formatos americanos
    '%m/%d/%Y %H:%M:%S', '%m/%d/%Y',
    # Formatos com nomes de mês, etc.
    '%d %b %Y', '%Y-%m-%d %H:%M:%S.%f',
]


def profile_dataframe(df):
    """
    Realiza o perfilamento de um DataFrame, analisando cada coluna.
    """
    profile_results = []

    for col_name in df.columns:
        column_series = df[col_name]

        col_profile = {
            "nome_coluna": col_name,
            "tipo_pandas": str(column_series.dtype),
            "tipo_inferido": "Indeterminado",
            "estatisticas": {
                "total_registros": len(column_series),
                "valores_nao_nulos": int(column_series.count()),
                "valores_ausentes": int(column_series.isnull().sum()),
                "percentual_ausentes": round(column_series.isnull().mean() * 100, 2),
                "valores_unicos": int(column_series.nunique())
            }
        }

        if col_profile["estatisticas"]["valores_nao_nulos"] == 0:
            col_profile["tipo_inferido"] = "Vazio"
            profile_results.append(col_profile)
            continue

        numeric_series = pd.to_numeric(column_series.dropna(), errors='coerce')
        if (numeric_series.count() / column_series.count()) > 0.8:
            col_profile["tipo_inferido"] = "Numérico"
            col_profile["estatisticas"].update({
                "min": float(numeric_series.min()), "max": float(numeric_series.max()),
                "media": float(numeric_series.mean()), "mediana": float(numeric_series.median()),
                "desvio_padrao": float(numeric_series.std()), "soma": float(numeric_series.sum()),
                "quantil_25": float(numeric_series.quantile(0.25)), "quantil_75": float(numeric_series.quantile(0.25)),
                "contagem_zeros": int((numeric_series == 0).sum())
            })

        elif col_profile["tipo_inferido"] == "Indeterminado":
            datetime_series = None
            detected_format = None

            # Tenta com formatos conhecidos para performance
            for date_format in COMMON_DATE_FORMATS:
                try:
                    temp_series = pd.to_datetime(
                        column_series.dropna(), format=date_format, errors='coerce')
                    if (temp_series.count() / column_series.count()) > 0.8:
                        datetime_series = temp_series
                        detected_format = date_format
                        break
                except (ValueError, TypeError):
                    continue

            # Se não funcionou, tenta o método lento do Pandas
            # if datetime_series is None:
            #    try:
            #        temp_series = pd.to_datetime(
            #            column_series.dropna(), errors='coerce')
            #        if (temp_series.count() / column_series.count()) > 0.8:
            #            datetime_series = temp_series
            #            detected_format = "Inferido (lento)"
            #    except Exception:
            #        datetime_series = None

            if datetime_series is not None:
                col_profile["tipo_inferido"] = "Data/Hora"
                col_profile["estatisticas"]["formato_data_detectado"] = detected_format
                earliest_date, latest_date = datetime_series.min(), datetime_series.max()
                col_profile["estatisticas"].update({
                    "data_minima": earliest_date.isoformat() if pd.notna(earliest_date) else None,
                    "data_maxima": latest_date.isoformat() if pd.notna(latest_date) else None,
                })

        if col_profile["tipo_inferido"] == "Indeterminado":
            if column_series.nunique() == 2:
                col_profile["tipo_inferido"] = "Booleano/Binário"
                value_counts = column_series.value_counts().to_dict()
                col_profile["estatisticas"]["distribuicao"] = {
                    str(k): int(v) for k, v in value_counts.items()}
            else:
                col_profile["tipo_inferido"] = "Categórico/Texto"

        if col_profile["tipo_inferido"] in ["Categórico/Texto", "Booleano/Binário"] or \
           (col_profile["tipo_inferido"] == "Numérico" and column_series.nunique() < 25):

            if "distribuicao" not in col_profile["estatisticas"]:
                top_5_counts = column_series.value_counts().nlargest(5).to_dict()
                col_profile["estatisticas"]["valores_mais_frequentes"] = {
                    str(k): int(v) for k, v in top_5_counts.items()}

        profile_results.append(col_profile)

    return profile_results


def main():
    # O código da função main permanece exatamente o mesmo da versão anterior.
    # A única mudança foi na lógica interna da função 'profile_dataframe'.
    parser = argparse.ArgumentParser(
        description="Realiza o perfilamento de dados por coluna para um conjunto de arquivos.",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument(
        "-d", "--root-directory", type=str, required=True,
        help="Diretório raiz para a busca dos arquivos de dados."
    )
    parser.add_argument(
        "-e", "--extensions", nargs='+', default=['csv', 'xlsx', 'xls', 'json'], type=str,
        help="Lista de extensões de arquivo a serem consideradas.\nPadrão: csv xlsx xls json"
    )
    parser.add_argument(
        "-r", "--recursive", action="store_true",
        help="Incluir subdiretórios na busca. Padrão: não incluir."
    )
    parser.add_argument(
        "--delimiter", type=str, default=",",
        help="Delimitador para arquivos CSV.\nPadrão: ',' (vírgula). Use '\\t' para TAB."
    )
    parser.add_argument(
        "-o", "--output-report", type=str, required=True,
        help="Caminho obrigatório para salvar o relatório de perfilamento em formato JSON."
    )

    args = parser.parse_args()

    actual_delimiter = args.delimiter.replace('\\t', '\t')

    try:
        root_dir_processed = os.path.abspath(
            os.path.expanduser(args.root_directory))
    except Exception as e:
        print(
            f"Erro Crítico: Falha ao processar o caminho do diretório raiz '{args.root_directory}': {e}")
        sys.exit(1)

    print("--- Configurações do Perfilamento de Dados ---")
    print(f"Diretório Raiz: {root_dir_processed}")
    print(f"Extensões Alvo: {', '.join(args.extensions)}")
    print(f"Buscar em Subdiretórios: {'Sim' if args.recursive else 'Não'}")
    print(f"Delimitador CSV: '{actual_delimiter}'")
    print(f"Relatório de Saída: {args.output_report}")
    print("----------------------------------------------\n")

    discovered_files = find_files(
        root_dir_processed, args.extensions, args.recursive)
    if not discovered_files:
        print("Nenhum arquivo encontrado com os critérios especificados.")
        sys.exit(0)

    print(
        f"Encontrados {len(discovered_files)} arquivo(s). Iniciando perfilamento...")

    full_report = []

    for file_path in discovered_files:
        relative_path = os.path.relpath(file_path, root_dir_processed)
        print(f"  Analisando: {relative_path} ...")

        _, file_ext_with_dot = os.path.splitext(file_path)
        extension = file_ext_with_dot.lstrip('.').lower()

        try:
            if extension == 'csv':
                df = pd.read_csv(
                    file_path, sep=actual_delimiter, low_memory=False)
                profile = profile_dataframe(df)
                full_report.append(
                    {"arquivo": relative_path, "perfil_colunas": profile})

            elif extension in ['xlsx', 'xls']:
                xls = pd.ExcelFile(file_path)
                for sheet_name in xls.sheet_names:
                    print(f"    -> Planilha: {sheet_name}")
                    df = pd.read_excel(xls, sheet_name=sheet_name)
                    profile = profile_dataframe(df)
                    full_report.append({
                        "arquivo": relative_path,
                        "planilha": sheet_name,
                        "perfil_colunas": profile
                    })

            elif extension == 'json':
                try:
                    df = pd.read_json(file_path, lines=True)
                except (ValueError, TypeError):
                    df = pd.read_json(file_path)
                profile = profile_dataframe(df)
                full_report.append(
                    {"arquivo": relative_path, "perfil_colunas": profile})

        except Exception as e:
            print(
                f"    ERRO: Não foi possível processar o arquivo '{relative_path}'. Causa: {e}")
            full_report.append({"arquivo": relative_path, "erro": str(e)})

    try:
        with open(args.output_report, 'w', encoding='utf-8') as f_out:
            json.dump(full_report, f_out, indent=2, ensure_ascii=False)
        print(
            f"\nRelatório de perfilamento salvo com sucesso em: {args.output_report}")
    except Exception as e:
        print(
            f"\nErro ao salvar o relatório final em '{args.output_report}': {e}")

    print("\nPerfilamento de dados concluído.")


if __name__ == "__main__":
    main()

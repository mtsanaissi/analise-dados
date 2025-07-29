# -*- coding: utf-8 -*-

# --------------------------------------------------------------------------------
# Descrição: Gera relatórios de perfilamento de dados com ydata-profiling
#            para múltiplos arquivos e os salva como arquivos HTML individuais.
# Exemplo de uso: python tool_generate_html_profiles.py --argumento valor
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
from ydata_profiling import ProfileReport
from src.utils import find_files, read_csv_robust


def generate_profiles(root_dir, output_dir, extensions, recursive, delimiter):
    """
    Gera relatórios de perfil de dados para arquivos em um diretório.

    Args:
        root_dir (str): O diretório raiz para procurar arquivos.
        output_dir (str): O diretório para salvar os relatórios HTML.
        extensions (list): Uma lista de extensões de arquivo a serem incluídas.
        recursive (bool): Se a busca por arquivos deve ser recursiva.
        delimiter (str): O delimitador a ser usado ao ler arquivos CSV.
    """
    os.makedirs(output_dir, exist_ok=True)

    if root_dir == output_dir:
        print("Erro: Diretório de entrada e saída não podem ser os mesmos.", file=sys.stderr)
        sys.exit(1)

    files_to_profile = find_files(root_dir, extensions, recursive)
    if not files_to_profile:
        print("Nenhum arquivo encontrado.")
        return

    print(f"Encontrados {len(files_to_profile)} arquivos. Gerando relatórios...")

    for file_path in files_to_profile:
        filename = os.path.basename(file_path)
        print(f"  -> Processando: {filename}")

        try:
            df = None
            if file_path.lower().endswith('.csv'):
                df = read_csv_robust(file_path, delimiter=delimiter.replace('\\t', '\t'))
            elif file_path.lower().endswith(('.xlsx', '.xls')):
                df = pd.read_excel(file_path, sheet_name=0)
            elif file_path.lower().endswith('.json'):
                df = pd.read_json(file_path)

            if df is not None:
                profile = ProfileReport(df, title=f"Relatório de Análise para {filename}")
                output_filename = f"{os.path.splitext(filename)[0]}_profile.html"
                output_path = os.path.join(output_dir, output_filename)
                profile.to_file(output_path)
                print(f"     Relatório salvo em: {output_path}")

        except Exception as e:
            print(f"     ERRO ao processar {filename}: {e}", file=sys.stderr)

    print("\nProcesso concluído.")


def main():
    """
    Função principal para executar a ferramenta a partir da linha de comando.
    """
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

    generate_profiles(
        root_dir=os.path.abspath(args.root_directory),
        output_dir=os.path.abspath(args.output_directory),
        extensions=args.extensions,
        recursive=args.recursive,
        delimiter=args.delimiter
    )


if __name__ == "__main__":
    main()

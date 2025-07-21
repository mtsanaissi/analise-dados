# -*- coding: utf-8 -*-

# --------------------------------------------------------------------------------
# Descrição: Este script varre arquivos CSV em um diretório e seus
#            subdiretórios para detectar o delimitador de cada arquivo.
#            Utiliza o csv.Sniffer do Python para a detecção.
# Exemplo de uso: python p1_03_detect_csv_delimiter.py --argumento valor
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
import csv
import chardet
import pandas as pd
from ..utils import find_files
from ..connectors.factory import get_data_loader


def detect_csv_delimiter(file_path, sample_size_bytes=20480):  # Amostra de 20KB
    """
    Detecta o delimitador de um arquivo CSV usando chardet e csv.Sniffer.

    Retorna:
        dict: Um dicionário com 'delimitador', 'encoding' e 'erro'.
    """
    result = {"delimitador": None, "encoding": None, "erro": None}

    # 1. Verifica se o arquivo está vazio
    if os.path.getsize(file_path) == 0:
        result["erro"] = "Arquivo vazio"
        return result

    # 2. Detecta o encoding
    try:
        with open(file_path, 'rb') as f_raw:
            raw_data = f_raw.read(sample_size_bytes)
            if not raw_data:
                result["erro"] = "Arquivo não contém dados para análise"
                return result

            detection = chardet.detect(raw_data)
            encoding = detection['encoding'] if detection['confidence'] > 0.7 else 'utf-8'
            # Guarda o encoding detectado
            result["encoding"] = detection['encoding']
    except Exception as e:
        result["erro"] = f"Falha ao ler para detectar encoding: {e}"
        return result

    if encoding is None:
        encoding = 'utf-8'  # Fallback final
        result["encoding"] = "utf-8 (fallback)"

    # 3. Usa o Sniffer para detectar o delimitador
    try:
        # Abre o arquivo no modo texto com o encoding detectado
        with open(file_path, 'r', encoding=encoding, errors='replace') as f_text:
            # O Sniffer precisa de uma amostra de texto
            # Lê menos para evitar cortar char multibyte
            sample_text = f_text.read(sample_size_bytes // 2)
            if not sample_text.strip():
                result["erro"] = "Amostra do arquivo contém apenas espaços em branco"
                return result

            # A mágica acontece aqui
            dialect = csv.Sniffer().sniff(sample_text)
            result["delimitador"] = dialect.delimiter
    except csv.Error:
        result["erro"] = "Sniffer não conseguiu determinar o delimitador (formato pode ser inconsistente)"
    except UnicodeDecodeError:
        result["erro"] = f"Erro de decodificação com o encoding '{encoding}'. O arquivo pode estar corrompido ou com outro encoding."
    except Exception as e:
        result["erro"] = f"Erro inesperado: {e}"

    return result


def main():
    parser = argparse.ArgumentParser(
        description="Detecta o delimitador de arquivos CSV em um diretório.",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument(
        "-d", "--root-directory",
        type=str,
        required=True,
        help="Diretório raiz para a busca dos arquivos CSV."
    )
    parser.add_argument(
        "-r", "--recursive",
        action="store_true",
        help="Incluir subdiretórios na busca. Padrão: não incluir."
    )
    parser.add_argument(
        "-o", "--output-report",
        type=str,
        help="Caminho opcional para salvar o relatório de delimitadores em formato CSV."
    )

    args = parser.parse_args()

    try:
        root_dir_processed = os.path.abspath(
            os.path.expanduser(args.root_directory))
    except Exception as e:
        print(
            f"Erro Crítico: Falha ao processar o caminho do diretório raiz '{args.root_directory}': {e}")
        sys.exit(1)

    print("--- Configurações da Detecção de Delimitador ---")
    print(f"Diretório Raiz: {root_dir_processed}")
    print(f"Buscar em Subdiretórios: {'Sim' if args.recursive else 'Não'}")
    print("------------------------------------------------\n")

    discovered_files = find_files(root_dir_processed, ['csv'], args.recursive)

    if not discovered_files:
        print("Nenhum arquivo CSV encontrado com os critérios especificados.")
        sys.exit(0)

    print(
        f"Encontrados {len(discovered_files)} arquivo(s) CSV. Iniciando detecção...\n")

    all_results = []

    # Cabeçalho para a impressão no console
    print(f"{'Arquivo':<60} | {'Delimitador Detectado':<25} | {'Encoding Sugerido'}")
    print("-" * 110)

    for file_path in discovered_files:
        relative_path = os.path.relpath(file_path, root_dir_processed)
        result = detect_csv_delimiter(file_path)

        # Prepara a representação do delimitador para impressão
        if result["delimitador"]:
            if result["delimitador"] == '\t':
                display_delimiter = "'\\t' (TAB)"
            else:
                display_delimiter = f"'{result['delimitador']}'"
        else:
            display_delimiter = result["erro"] or "Não detectado"

        all_results.append({
            "arquivo": relative_path,
            "delimitador": result["delimitador"],
            "encoding_sugerido": result["encoding"],
            "observacao": result["erro"]
        })

        # Imprime o resultado para o arquivo atual
        print(
            f"{relative_path:<60} | {display_delimiter:<25} | {result['encoding'] or 'N/A'}")

    if args.output_report:
        try:
            df_report = pd.DataFrame(all_results)
            # Utiliza a fábrica para obter o conector e salvar o relatório
            report_connector = get_data_loader(args.output_report)
            report_connector.write(df_report, encoding='utf-8-sig')
            print(
                f"\nRelatório de detecção salvo com sucesso em: {args.output_report}")
        except Exception as e:
            print(
                f"\nErro ao salvar o relatório em '{args.output_report}': {e}")

    print("\nDetecção de delimitadores concluída.")


if __name__ == "__main__":
    main()

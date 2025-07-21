# -*- coding: utf-8 -*-

# --------------------------------------------------------------------------------
# Descrição: Script para conferir consistência de colunas de cabeçalho de arquivos CSV.
# Exemplo de uso: python p1_04_check_column_consistency.py
#
# Autor: Marcelo Anaissi
# Criado em: 2025-05-28
# Versão: 1.1
#
# Modificado por: Jules
# Modificado em: 21/07/2025
# Licença: MIT
# --------------------------------------------------------------------------------


import os
import argparse
from pathlib import Path
from ..utils import find_files
from ..connectors.factory import get_data_loader


def get_csv_header(filepath):
    """
    Lê o cabeçalho de um arquivo CSV usando o conector de dados.
    Retorna a lista de colunas do cabeçalho ou uma string de erro.
    """
    try:
        # Utiliza a fábrica para obter o conector apropriado
        data_loader = get_data_loader(filepath)
        # Lê o arquivo CSV. A lógica de detecção de encoding/delimitador
        # pode ser adicionada ao conector ou passada como kwargs.
        # Por enquanto, assumimos que o conector lida com isso.
        df = data_loader.read()

        if df is None:
            return "READ_ERROR: Falha na leitura do arquivo (ver logs de erro)."

        if df.empty:
            # Distingue entre um arquivo vazio e um sem colunas
            if len(df.columns) == 0:
                return None  # Arquivo realmente vazio
            else:
                # Arquivo com cabeçalho mas sem dados
                return [str(col).strip() for col in df.columns]

        return [str(col).strip() for col in df.columns]

    except FileNotFoundError:
        return "FILE_NOT_FOUND_ERROR"
    except ValueError as e: # Captura o erro da factory
        return f"CONNECTOR_ERROR: {e}"
    except Exception as e:
        return f"GENERAL_ERROR: {e}"


def check_csv_structures(root_directory):
    """
    Verifica se todos os arquivos CSV em um diretório (e subdiretórios)
    possuem a mesma estrutura de cabeçalho.
    """
    if not os.path.isdir(root_directory):
        print(
            f"Erro: O diretório '{root_directory}' não existe ou não é um diretório.")
        return False, None, {"error": "Directory not found"}

    csv_files = find_files(root_directory, ['csv'], recursive=True)
    # Ordena para garantir uma ordem de processamento consistente
    csv_files.sort()

    if not csv_files:
        print(
            f"Nenhum arquivo .csv encontrado em '{root_directory}' e suas subpastas.")
        return True, None, {}

    reference_header = None
    reference_filepath = None
    # Dicionário para armazenar {filepath: "motivo da inconsistência"}
    inconsistent_files = {}
    consistent_files_count = 0

    print(
        f"Iniciando verificação de estrutura de {len(csv_files)} arquivos CSV em '{root_directory}'...\n")

    for filepath in csv_files:
        relative_path = os.path.relpath(filepath, root_directory)
        print(f"Analisando: {relative_path}")

        current_header_or_error = get_csv_header(filepath)

        if isinstance(current_header_or_error, str):  # Indica um código de erro
            error_message = current_header_or_error
            if error_message == "FILE_NOT_FOUND_ERROR":
                inconsistent_files[str(
                    relative_path)] = "Arquivo não encontrado durante a leitura do cabeçalho (pode ter sido removido)."
            elif error_message == "DECODING_ERROR":
                inconsistent_files[str(
                    relative_path)] = "Não foi possível decodificar o arquivo com os encodings padrão."
            elif error_message.startswith("GENERAL_ERROR:"):
                inconsistent_files[str(
                    relative_path)] = f"Erro geral ao ler o arquivo: {error_message.split(':', 1)[1].strip()}"
            else:  # Caso inesperado
                inconsistent_files[str(
                    relative_path)] = f"Erro desconhecido ao obter cabeçalho: {error_message}"
            continue

        current_header = current_header_or_error

        if current_header is None:
            print(
                f"  -> AVISO: Arquivo CSV está vazio ou não contém cabeçalho: {relative_path}")
            inconsistent_files[str(relative_path)
                               ] = "CSV vazio ou sem cabeçalho."
            continue

        if reference_header is None:
            reference_header = current_header
            reference_filepath = relative_path
            print(
                f"  -> Cabeçalho de REFERÊNCIA definido a partir de: {reference_filepath}")
            print(
                f"     Colunas ({len(reference_header)}): {reference_header}")
            consistent_files_count += 1
        else:
            if len(current_header) != len(reference_header):
                msg = (f"Número de colunas diferente. Esperado: {len(reference_header)}, "
                       f"Encontrado: {len(current_header)}.")
                print(f"  -> INCONSISTENTE: {msg}")
                print(f"     Esperado: {reference_header}")
                print(f"     Encontrado: {current_header}")
                inconsistent_files[str(relative_path)] = msg
            elif current_header != reference_header:
                # Encontrar a primeira diferença para dar uma dica melhor
                diff_reason = "Nomes/ordem das colunas diferente."
                for i, (ref_col, cur_col) in enumerate(zip(reference_header, current_header)):
                    if ref_col != cur_col:
                        diff_reason = (f"Diferença na coluna {i+1}. "
                                       f"Esperado: '{ref_col}', Encontrado: '{cur_col}'.")
                        break
                print(f"  -> INCONSISTENTE: {diff_reason}")
                print(f"     Esperado: {reference_header}")
                print(f"     Encontrado: {current_header}")
                inconsistent_files[str(relative_path)] = diff_reason
            else:
                print("  -> OK: Estrutura consistente.")
                consistent_files_count += 1
        print("-" * 30)

    print("\n--- Relatório Final ---")
    if reference_header is None and not inconsistent_files:
        print("Nenhum cabeçalho de referência pôde ser definido (talvez todos os arquivos CSV estejam vazios ou com erro).")
    elif reference_header:
        print(
            f"Cabeçalho de Referência (de '{reference_filepath}', {len(reference_header)} colunas):")
        print(f"  {reference_header}")

    if not inconsistent_files:
        if consistent_files_count > 0:
            print(
                f"\nTODOS os {consistent_files_count} arquivos CSV analisados possuem a MESMA estrutura!")
        elif not csv_files:
            pass  # Mensagem de "nenhum arquivo" já foi dada
        else:
            print(
                "\nNenhum arquivo CSV pôde ser comparado efetivamente (verifique erros acima).")

    else:
        print(
            f"\nATENÇÃO: {len(inconsistent_files)} arquivo(s) com estrutura INCONSISTENTE ou erros:")
        for f, reason in inconsistent_files.items():
            print(f"  - {f}: {reason}")
        print(f"\nTotal de arquivos consistentes: {consistent_files_count}")

    return not bool(inconsistent_files), reference_header, inconsistent_files


def main():
    """
    Função principal para analisar argumentos da linha de comando e
    iniciar a verificação da estrutura dos CSVs.
    """
    parser = argparse.ArgumentParser(
        description="Verifica a consistência da estrutura de colunas em múltiplos arquivos CSV.",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument(
        "-d", "--directory",
        type=str,
        required=True,
        help="Diretório raiz para a busca dos arquivos CSV."
    )
    args = parser.parse_args()

    root_dir = args.directory
    
    if not os.path.isdir(root_dir):
        print(f"Erro: O diretório especificado '{root_dir}' não existe.")
    else:
        print(f"Usando diretório: {Path(root_dir).resolve()}")
        check_csv_structures(root_dir)

if __name__ == "__main__":
    main()

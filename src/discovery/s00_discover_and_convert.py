#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ----------------------------------------------------------------------------
# Script: discover_and_convert.py
# Autor: Marcelo Anaissi
# Data: 29/05/2025
# Versão: 2.0
# Licença: (Se aplicável, ex: MIT, GPL, etc.)
# Descrição: Este script localiza arquivos em um diretório com base em
#            extensões fornecidas. Após a localização, ele verifica
#            o encoding de cada arquivo de texto e converte
#            automaticamente para UTF-8 aqueles que não estiverem nesse formato.
#
# Requisito: A biblioteca 'chardet' precisa ser instalada.
#            Execute: pip install chardet
# ----------------------------------------------------------------------------

import os
import argparse
import sys
import chardet  # Importa a biblioteca para detecção de encoding
from ..utils import find_files # Importa a função centralizada

# Lista de extensões que são tipicamente binárias e não devem ser convertidas
BINARY_EXTENSIONS = ['xlsx', 'xls', 'ods', 'doc',
                     'docx', 'pdf', 'zip', 'gz', 'png', 'jpg']


def detect_encoding(file_path):
    """
    Tenta detectar o encoding de um arquivo lendo os primeiros 100KB.
    """
    print(f"  Analisando encoding de: {os.path.basename(file_path)}")
    try:
        with open(file_path, 'rb') as f:  # Abre em modo binário
            raw_data = f.read(102400)  # Lê os primeiros 100KB
            result = chardet.detect(raw_data)
            encoding = result['encoding']
            confidence = result.get('confidence', 0)

            if encoding:
                print(
                    f"  -> Detecado: {encoding} (Confiança: {confidence:.0%})")
            else:
                print("  -> Não foi possível detectar o encoding.")
                return None

            # Se a confiança for muito baixa, é mais seguro usar um padrão comum
            if confidence < 0.7:
                print("  -> Confiança baixa. Usando 'latin-1' como alternativa segura.")
                return 'latin-1'

            return encoding

    except FileNotFoundError:
        print(f"  -> Erro: Arquivo não encontrado durante a detecção de encoding.")
        return None
    except Exception as e:
        print(f"  -> Erro ao ler o arquivo para detecção: {e}")
        return None


def convert_file_to_utf8(file_path, source_encoding):
    """
    Converte um arquivo para UTF-8 de forma segura.
    1. Renomeia o original para .bak (backup).
    2. Lê do backup com o encoding original e escreve no novo arquivo com UTF-8.
    3. Se falhar, restaura o backup.
    """
    backup_path = str(file_path) + ".bak"
    print(
        f"  Iniciando conversão para UTF-8. Backup será criado em: {os.path.basename(backup_path)}")

    try:
        # Passo 1: Criar o backup
        os.rename(file_path, backup_path)

        # Passo 2: Ler do backup e escrever no original com o novo encoding
        with open(backup_path, 'r', encoding=source_encoding, errors='replace') as infile, \
                open(file_path, 'w', encoding='utf-8') as outfile:
            for line in infile:
                outfile.write(line)

        print(
            f"  -> SUCESSO: Arquivo '{os.path.basename(file_path)}' convertido para UTF-8.")
        # Opcional: remover o backup após o sucesso. Por segurança, é melhor mantê-lo.
        # os.remove(backup_path)

    except Exception as e:
        print(f"  -> ERRO na conversão: {e}")
        print("  -> Restaurando arquivo original a partir do backup.")
        # Se a conversão falhar, restaura o arquivo original
        os.rename(backup_path, file_path)
        return False

    return True


def main():
    """
    Função principal para configurar o parser, buscar arquivos, e
    depois verificar e converter o encoding desses arquivos.
    """
    parser = argparse.ArgumentParser(
        description="Ferramenta para descobrir arquivos, verificar e converter seu encoding para UTF-8.",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument(
        "-d", "--root-directory", type=str, required=True,
        help="Diretório raiz para a busca dos arquivos de dados."
    )
    parser.add_argument(
        "-e", "--extensions", nargs='+', default=['csv', 'txt', 'json', 'xml'],
        type=str,
        help="Lista de extensões a serem consideradas (sem o ponto).\nPadrão: csv txt json xml"
    )
    parser.add_argument(
        "-r", "--recursive", action="store_true",
        help="Incluir subdiretórios na busca."
    )
    args = parser.parse_args()

    try:
        root_dir_processed = os.path.abspath(
            os.path.expanduser(args.root_directory))
    except Exception as e:
        print(
            f"Erro ao processar o caminho do diretório raiz '{args.root_directory}': {e}")
        sys.exit(1)

    print("--- Configurações da Ferramenta ---")
    print(f"Diretório Raiz Alvo: {root_dir_processed}")
    print(f"Extensões Procuradas: {', '.join(args.extensions)}")
    print(f"Buscar em Subdiretórios: {'Sim' if args.recursive else 'Não'}")
    print("-----------------------------------\n")

    # Passo 1: Descobrir os arquivos usando a função centralizada
    print(f"Iniciando busca em: {root_dir_processed}")
    discovered_files = find_files(
        root_dir_processed, args.extensions, args.recursive)

    if not discovered_files:
        print("Nenhum arquivo encontrado com os critérios especificados.")
        return

    print(
        f"\n--- Fase 1: Busca concluída. {len(discovered_files)} arquivo(s) encontrado(s). ---\n")

    # Passo 2: Verificar e converter o encoding de cada arquivo encontrado
    print("--- Fase 2: Iniciando Verificação e Conversão de Encoding ---\n")
    converted_count = 0
    skipped_count = 0
    for file_path in discovered_files:
        print(f"Processando arquivo: {file_path}")

        # Pega a extensão para verificar se é um arquivo binário
        _, file_ext_with_dot = os.path.splitext(file_path)
        file_extension = file_ext_with_dot.lstrip('.').lower()

        if file_extension in BINARY_EXTENSIONS:
            print(
                "  -> Arquivo com extensão binária conhecida. Pulando verificação de encoding.\n")
            skipped_count += 1
            continue

        # Detecta o encoding
        encoding = detect_encoding(file_path)

        if not encoding:
            print("  -> Não foi possível determinar o encoding. Pulando arquivo.\n")
            skipped_count += 1
            continue

        # Verifica se já está em UTF-8
        if encoding.lower() in ['utf-8', 'ascii', 'utf-8-sig']:
            print("  -> O arquivo já está no formato UTF-8. Nenhuma ação necessária.\n")
            skipped_count += 1
            continue

        # Se não for UTF-8, converte
        if convert_file_to_utf8(file_path, encoding):
            converted_count += 1
        else:
            skipped_count += 1  # Conta como pulado se a conversão falhar
        print("")  # Adiciona uma linha em branco para legibilidade

    print("--- Processo Finalizado ---")
    print(f"Resumo: {converted_count} arquivo(s) convertido(s) para UTF-8.")
    print(
        f"        {skipped_count} arquivo(s) pulado(s) (já em UTF-8, binários ou com erro).")
    print("Para arquivos convertidos, um backup (.bak) do original foi mantido no mesmo diretório.")


if __name__ == "__main__":
    main()

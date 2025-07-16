#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ----------------------------------------------------------------------------
# Módulo: utils.py
# Autor: Gemini
# Data: 15/07/2025
# Versão: 1.0
# Licença: (Se aplicável)
# Descrição: Este módulo centraliza funções de utilidade reutilizáveis
#            para o projeto de análise de dados, como descoberta de arquivos,
#            leitura e gravação de dados, e verificações de qualidade.
# ----------------------------------------------------------------------------

import os
import sys
import pandas as pd
import chardet
import csv

def find_files(root_path: str, extensions: list[str], recursive: bool = True) -> list[str]:
    """
    Encontra arquivos em um diretório com base em uma lista de extensões.

    Args:
        root_path (str): O diretório raiz para a busca.
        extensions (list[str]): Uma lista de extensões de arquivo (sem o ponto).
        recursive (bool): Se True, busca recursivamente em subdiretórios.

    Returns:
        list[str]: Uma lista de caminhos absolutos para os arquivos encontrados.
    """
    found_files = []
    normalized_extensions = [ext.lower().lstrip('.') for ext in extensions]
    
    if not os.path.isdir(root_path):
        print(f"Erro: O diretório raiz '{root_path}' não existe ou não é um diretório.", file=sys.stderr)
        return found_files

    if recursive:
        for dirpath, _, filenames in os.walk(root_path):
            for filename in filenames:
                _, file_ext_with_dot = os.path.splitext(filename)
                file_extension = file_ext_with_dot.lstrip('.').lower()
                if file_extension in normalized_extensions:
                    found_files.append(os.path.abspath(os.path.join(dirpath, filename)))
    else:
        try:
            for filename in os.listdir(root_path):
                full_path = os.path.join(root_path, filename)
                if os.path.isfile(full_path):
                    _, file_ext_with_dot = os.path.splitext(filename)
                    file_extension = file_ext_with_dot.lstrip('.').lower()
                    if file_extension in normalized_extensions:
                        found_files.append(os.path.abspath(full_path))
        except PermissionError:
            print(f"Erro de Permissão: Não foi possível acessar o diretório '{root_path}'.", file=sys.stderr)
        except OSError as e:
            print(f"Erro de SO ao listar arquivos no diretório '{root_path}': {e}", file=sys.stderr)

    return found_files

def read_csv_robust(file_path: str, delimiter: str = ';') -> pd.DataFrame | None:
    """
    Lê um arquivo CSV de forma robusta, tentando detectar o encoding.

    Args:
        file_path (str): O caminho para o arquivo CSV.
        delimiter (str): O delimitador a ser usado.

    Returns:
        pd.DataFrame | None: O DataFrame lido ou None em caso de erro.
    """
    try:
        # Detectar encoding com uma amostra
        with open(file_path, 'rb') as f_raw:
            raw_data = f_raw.read(50 * 1024)  # Amostra de 50KB
            detection = chardet.detect(raw_data)
            encoding = detection['encoding'] if detection['confidence'] > 0.7 else 'utf-8'

        # Ler o CSV com o encoding detectado ou fallback para utf-8 com replace
        try:
            df = pd.read_csv(file_path, sep=delimiter, encoding=encoding, low_memory=False)
        except UnicodeDecodeError:
            print(f"  Aviso: Falha ao ler '{os.path.basename(file_path)}' com encoding '{encoding}'. Tentando com 'utf-8' e 'replace'.")
            df = pd.read_csv(file_path, sep=delimiter, encoding='utf-8', errors='replace', low_memory=False)
        
        return df

    except FileNotFoundError:
        print(f"Erro: Arquivo não encontrado em '{file_path}'.", file=sys.stderr)
        return None
    except pd.errors.EmptyDataError:
        print(f"Aviso: Arquivo CSV vazio ou sem dados: {os.path.basename(file_path)}", file=sys.stderr)
        return pd.DataFrame() # Retorna DF vazio para consistência
    except Exception as e:
        print(f"Erro inesperado ao ler o arquivo '{os.path.basename(file_path)}': {e}", file=sys.stderr)
        return None

def has_problematic_char(text_value: any) -> bool:
    """
    Verifica se uma string contém caracteres problemáticos.
    Problemáticos: Unicode Replacement Character (U+FFFD) ou caracteres de controle
                   não padrão (diferentes de tab, newline, carriage return).
    
    Args:
        text_value (any): O valor a ser verificado.

    Returns:
        bool: True se contiver caracteres problemáticos, False caso contrário.
    """
    if not isinstance(text_value, str):
        return False

    control_chars_allowed = {'\t', '\n', '\r'}
    for char_read in text_value:
        if char_read == '\ufffd':  # Caractere de substituição Unicode
            return True
        # Verifica caracteres de controle não permitidos
        if not char_read.isprintable() and char_read not in control_chars_allowed:
            return True
    return False

def save_df_to_csv(df: pd.DataFrame, output_path: str, delimiter: str = ';') -> bool:
    """
    Salva um DataFrame em um arquivo CSV de forma padronizada.

    Args:
        df (pd.DataFrame): O DataFrame a ser salvo.
        output_path (str): O caminho do arquivo de saída.
        delimiter (str): O delimitador a ser usado.

    Returns:
        bool: True se o arquivo foi salvo com sucesso, False caso contrário.
    """
    try:
        # Garante que o diretório de saída exista
        output_dir = os.path.dirname(output_path)
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
        
        # Salva o DataFrame com encoding utf-8-sig e sem o índice
        df.to_csv(output_path, sep=delimiter, index=False, encoding='utf-8-sig', quoting=csv.QUOTE_MINIMAL)
        return True
    except Exception as e:
        print(f"Erro ao salvar o arquivo CSV em '{output_path}': {e}", file=sys.stderr)
        return False

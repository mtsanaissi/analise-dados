# -*- coding: utf-8 -*-

# --------------------------------------------------------------------------------
# Descrição: Este módulo centraliza funções de utilidade reutilizáveis
#            para o projeto de análise de dados, como descoberta de arquivos,
#            leitura e gravação de dados, e verificações de qualidade.
# Exemplo de uso: import utils
#
# Autor: Gemini
# Criado em: 15/07/2025
# Versão: 1.1
#
# Modificado por: Jules
# Modificado em: 21/07/2025
# Licença: MIT
# --------------------------------------------------------------------------------

import os
import sys
import pandas as pd
import chardet
import csv
import fnmatch
import yaml
import logging

METADATA_DIR = "fad-metadados"

def find_files(root_path: str, extensions: list[str], recursive: bool = True, exclude_patterns: list[str] = None, exclude_dirs: list[str] = None) -> list[str]:
    """
    Encontra arquivos em um diretório com base em uma lista de extensões,
    com a opção de excluir arquivos que correspondem a determinados padrões e diretórios.
    Por padrão, ignora os diretórios 'fad-metadados', 'fad-config' e 'fad-bkp*'.

    Args:
        root_path (str): O diretório raiz para a busca.
        extensions (list[str]): Uma lista de extensões de arquivo (sem o ponto).
        recursive (bool): Se True, busca recursivamente em subdiretórios.
        exclude_patterns (list[str], optional): Uma lista de padrões de nome de arquivo
                                                  a serem excluídos (ex: ['*_report.json', 'temp_*']).
        exclude_dirs (list[str], optional): Uma lista de nomes de diretório a serem ignorados.
                                              Se None, usa a lista padrão:
                                              ['fad-metadados', 'fad-config', 'fad-bkp*'].

    Returns:
        list[str]: Uma lista de caminhos absolutos para os arquivos encontrados.
    """
    found_files = []
    normalized_extensions = [ext.lower().lstrip('.') for ext in extensions]
    exclude_patterns = exclude_patterns or []

    final_exclude_dirs = ['fad-metadados', 'fad-config', 'fad-bkp*']
    if exclude_dirs is not None:
        final_exclude_dirs.extend(exclude_dirs)

    if not os.path.isdir(root_path):
        print(f"Erro: O diretório raiz '{root_path}' não existe ou não é um diretório.", file=sys.stderr)
        return found_files

    if recursive:
        for dirpath, dirnames, filenames in os.walk(root_path):
            original_dirnames = list(dirnames)
            dirnames[:] = []
            for d in original_dirnames:
                if not any(fnmatch.fnmatch(d, pattern) for pattern in final_exclude_dirs):
                    dirnames.append(d)

            for filename in filenames:
                if any(fnmatch.fnmatch(filename, pattern) for pattern in exclude_patterns):
                    continue

                _, file_ext_with_dot = os.path.splitext(filename)
                file_extension = file_ext_with_dot.lstrip('.').lower()
                if file_extension in normalized_extensions:
                    found_files.append(os.path.abspath(os.path.join(dirpath, filename)))
    else:
        try:
            for filename in os.listdir(root_path):
                if any(fnmatch.fnmatch(filename, pattern) for pattern in exclude_patterns):
                    continue

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
        with open(file_path, 'rb') as f_raw:
            raw_data = f_raw.read(50 * 1024)
            detection = chardet.detect(raw_data)
            encoding = detection['encoding'] if detection['confidence'] > 0.7 else 'utf-8'

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
        return pd.DataFrame()
    except Exception as e:
        print(f"Erro inesperado ao ler o arquivo '{os.path.basename(file_path)}': {e}", file=sys.stderr)
        return None

def has_problematic_char(text_value: any) -> bool:
    """
    Verifica se uma string contém caracteres problemáticos.
    Problemáticos: Unicode Replacement Character (U+FFFD), o caractere '¬'
                   ou caracteres de controle não padrão (diferentes de tab,
                   newline, carriage return).
    
    Args:
        text_value (any): O valor a ser verificado.

    Returns:
        bool: True se contiver caracteres problemáticos, False caso contrário.
    """
    if not isinstance(text_value, str):
        return False

    problematic_chars = {'\ufffd', '¬'}
    control_chars_allowed = {'\t', '\n', '\r'}

    for char_read in text_value:
        if char_read in problematic_chars:
            return True
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
        output_dir = os.path.dirname(output_path)
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
        
        df.to_csv(output_path, sep=delimiter, index=False, encoding='utf-8-sig', quoting=csv.QUOTE_MINIMAL)
        return True
    except Exception as e:
        print(f"Erro ao salvar o arquivo CSV em '{output_path}': {e}", file=sys.stderr)
        return False

def build_command(
    project_path: str,
    phase: str,
    discovery_args: dict = None,
    treatment_args: dict = None
) -> list[str]:
    """
    Constrói a lista de argumentos do comando para o subprocesso.

    Args:
        project_path (str): O caminho para o projeto de dados.
        phase (str): A fase do projeto a ser executada.
        discovery_args (dict, optional): Argumentos para a fase de descoberta.
        treatment_args (dict, optional): Argumentos para a fase de tratamento.

    Returns:
        list[str]: A lista de argumentos do comando.
    """
    python_executable = sys.executable
    run_script_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'run.py'))

    command = [
        python_executable,
        run_script_path,
        "-d", project_path,
        "-p", phase
    ]

    if phase == "discovery" and discovery_args:
        if discovery_args.get("compare_fields"):
            command.append("--compare-fields")
        if discovery_args.get("compare_types"):
            command.append("--compare-types")
        if discovery_args.get("report_output"):
            command.extend(["--report-output", discovery_args["report_output"]])
        if discovery_args.get("char_cleanup_path"):
            command.extend(["--generate-char-cleanup-config", discovery_args["char_cleanup_path"]])

    if phase == "treatment" and treatment_args:
        operation_map = {
            "Remover Espaços": "--strip-whitespace",
            "Substituir Valores": "--replace-values",
            "Encontrar e Substituir Texto": "--find-and-replace-text",
            "Concatenar Dados": "--concatenate-data",
            "Enriquecer Dados": "--enrich-data"
        }
        operation = treatment_args.get("operation")
        if operation in operation_map:
            command.append(operation_map[operation])

            if operation == "Enriquecer Dados":
                for arg_name in ["main_file", "lookup_file", "main_key", "lookup_key", "output_file"]:
                    if treatment_args.get(arg_name):
                        command.extend([f"--{arg_name.replace('_', '-')}", treatment_args[arg_name]])
                if treatment_args.get("columns_to_add"):
                    command.extend(["--columns-to-add"] + treatment_args["columns_to_add"])

            elif operation == "Concatenar Dados":
                for arg_name in ["input_folder", "output_file", "file_type"]:
                    if treatment_args.get(arg_name):
                        command.extend([f"--{arg_name.replace('_', '-')}", treatment_args[arg_name]])

            elif operation in ["Substituir Valores", "Encontrar e Substituir Texto"]:
                config_path = treatment_args.get("config_file_path")
                if config_path:
                    command.append(config_path)

    return command

def read_yaml_config(file_path: str) -> dict | None:
    """
    Lê um arquivo de configuração YAML de forma robusta.

    Args:
        file_path (str): O caminho para o arquivo YAML.

    Returns:
        dict | None: O conteúdo do arquivo YAML como um dicionário, ou None em caso de erro.
    """
    try:
        with open(file_path, 'r', encoding='utf-8-sig') as f:
            config = yaml.safe_load(f)
            return config
    except FileNotFoundError:
        logging.error(f"Arquivo de configuração não encontrado em: {file_path}")
        return None
    except yaml.YAMLError as e:
        logging.error(f"Erro ao processar o arquivo YAML '{os.path.basename(file_path)}': {e}")
        return None
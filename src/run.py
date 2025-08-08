# -*- coding: utf-8 -*-

# --------------------------------------------------------------------------------
# Descrição: Ponto de entrada principal da CLI para o toolkit de análise de dados.
#            Este script utiliza argparse para fornecer sub-comandos para as
#            diferentes fases do processo (discovery, treatment).
# Exemplo de uso:
#   python src/run.py discovery --data-project-path ./data/sample
#   python src/run.py treatment enrich --main-file ./data/sample/f1.csv ...
#
# Autor: Jules
# Criado em: 08/08/2025
# Versão: 1.0
#
# Modificado por: Jules
# Modificado em: 08/08/2025
# Licença: MIT
# --------------------------------------------------------------------------------

import argparse
import logging
import os
import sys
from typing import Dict, Any

# Adiciona o diretório 'src' ao sys.path para importações corretas
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import yaml
import re
import pandas as pd
from src.utils import find_files

# --- Importações das funções de lógica ---
from src.phases.phase01_discovery.phase01_orchestrator import run_discovery_logic
from src.phases.phase02_treatment.core.data_enricher import enrich_data
from src.phases.phase02_treatment.core.value_corrector import correct_values
from src.phases.phase02_treatment.core.text_replacer import replace_text
from src.phases.phase02_treatment.core.whitespace_remover import remove_whitespace
from src.phases.phase02_treatment.core.column_transformer import transform_columns
from src.phases.phase02_treatment.core.data_concatenator import concatenate_data


def setup_logging():
    """Configura o logging básico para a aplicação."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )


def handle_result(result: Dict[str, Any]):
    """
    Imprime a mensagem e o caminho do relatório do dicionário de resultado.

    Args:
        result (Dict[str, Any]): O dicionário retornado pela função de lógica.
    """
    if not isinstance(result, dict):
        logging.error(f"O resultado esperado era um dicionário, mas foi recebido: {type(result)}")
        return

    message = result.get("message")
    report_path = result.get("report_path")

    if message:
        print(message)
    if report_path:
        print(f"Relatório gerado em: {report_path}")


def main():
    """
    Função principal que configura e executa o parser de argumentos da CLI.
    """
    setup_logging()

    parser = argparse.ArgumentParser(
        description="Ferramenta de linha de comando para análise e tratamento de dados."
    )
    subparsers = parser.add_subparsers(dest="command", required=True, help="Comandos disponíveis")

    # --- Parser para o comando 'discovery' ---
    parser_discovery = subparsers.add_parser("discovery", help="Executa a fase de descoberta e diagnóstico.")
    parser_discovery.add_argument(
        "--data-project-path",
        required=True,
        help="Caminho para o diretório do projeto de dados."
    )
    parser_discovery.add_argument(
        "--extensions",
        nargs='+',
        default=['csv', 'xlsx', 'xls', 'json', 'txt'],
        help="Lista de extensões de arquivo a serem analisadas."
    )
    parser_discovery.add_argument(
        "--no-recursive",
        action="store_false",
        dest="recursive",
        help="Desativa a busca recursiva por arquivos."
    )
    parser_discovery.add_argument(
        "--output-format",
        default="text",
        choices=["text", "interactive"],
        help="Formato da saída no console."
    )
    parser_discovery.add_argument(
        "--report-output",
        default="json",
        choices=["json", "html", "none"],
        help="Formato do arquivo de relatório gerado."
    )
    parser_discovery.add_argument(
        "--compare-fields",
        action="store_true",
        help="Ativa a comparação de estrutura entre arquivos."
    )
    parser_discovery.add_argument(
        "--compare-types",
        action="store_true",
        help="Ativa a comparação de tipos de dados entre arquivos."
    )
    parser_discovery.add_argument(
        "--generate-char-cleanup-config",
        metavar="CONFIG_PATH",
        help="Gera um arquivo de configuração (.yml) para a limpeza de caracteres problemáticos no caminho especificado."
    )

    # --- Parser para o comando 'treatment' ---
    parser_treatment = subparsers.add_parser("treatment", help="Executa a fase de tratamento de dados.")
    treatment_subparsers = parser_treatment.add_subparsers(dest="treatment_command", required=True, help="Operações de tratamento")

    # (Sub-comandos do treatment serão adicionados aqui)
    # --- Enrich ---
    parser_enrich = treatment_subparsers.add_parser("enrich", help="Enriquece um arquivo de dados com base em outro.")
    parser_enrich.add_argument("--main-file", required=True, help="Caminho para o arquivo principal a ser enriquecido.")
    parser_enrich.add_argument("--lookup-file", required=True, help="Caminho para o arquivo de consulta (lookup).")
    parser_enrich.add_argument("--main-key", required=True, help="Nome da coluna chave no arquivo principal.")
    parser_enrich.add_argument("--lookup-key", required=True, help="Nome da coluna chave no arquivo de consulta.")
    parser_enrich.add_argument("--columns-to-add", nargs='+', required=True, help="Nomes das colunas a serem adicionadas do arquivo de consulta.")
    parser_enrich.add_argument("--output-file", required=True, help="Caminho para salvar o arquivo de saída enriquecido.")
    parser_enrich.add_argument("--join-how", default="left", choices=["left", "right", "outer", "inner"], help="Tipo de junção a ser realizada.")
    parser_enrich.add_argument("--sep", default=",", help="Delimitador dos arquivos CSV.")

    # --- Correct Values ---
    parser_correct = treatment_subparsers.add_parser("correct_values", help="Corrige valores em colunas específicas com base em um arquivo de mapeamento.")
    parser_correct.add_argument("--data-project-path", required=True, help="Caminho para o diretório do projeto de dados.")
    parser_correct.add_argument("--config-file", required=True, help="Caminho para o arquivo de configuração YAML com as regras de correção.")

    # --- Replace Text ---
    parser_replace = treatment_subparsers.add_parser("replace_text", help="Substitui textos em colunas específicas com base em um arquivo de configuração.")
    parser_replace.add_argument("--data-project-path", required=True, help="Caminho para o diretório do projeto de dados.")
    parser_replace.add_argument("--config-file", required=True, help="Caminho para o arquivo de configuração YAML com as regras de substituição.")

    # --- Remove Whitespace ---
    parser_whitespace = treatment_subparsers.add_parser("remove_whitespace", help="Remove espaços em branco do início e fim dos valores em colunas de texto.")
    parser_whitespace.add_argument("--data-project-path", required=True, help="Caminho para o diretório do projeto de dados.")

    # --- Transform Columns ---
    parser_transform = treatment_subparsers.add_parser("transform_columns", help="Aplica transformações (renomear, excluir) em colunas.")
    parser_transform.add_argument("--data-project-path", required=True, help="Caminho para o diretório do projeto de dados.")

    # --- Concatenate Files ---
    parser_concat = treatment_subparsers.add_parser("concatenate", help="Concatena múltiplos arquivos em um único arquivo de saída.")
    parser_concat.add_argument("--data-project-path", required=True, help="Caminho para o diretório do projeto de dados.")
    parser_concat.add_argument("--output-file", required=True, help="Caminho para o arquivo de saída concatenado.")
    parser_concat.add_argument("--file-type", required=True, choices=["csv", "xlsx"], help="Tipo de arquivo a ser concatenado.")


    args = parser.parse_args()

    # --- Lógica de despacho ---
    if args.command == "discovery":
        result = run_discovery_logic(
            data_project_path=args.data_project_path,
            extensions=args.extensions,
            recursive=args.recursive,
            output_format=args.output_format,
            report_output=args.report_output,
            compare_fields=args.compare_fields,
            compare_types=args.compare_types,
            generate_char_cleanup_config=args.generate_char_cleanup_config
        )
        handle_result(result)
    elif args.command == "treatment":
        result = None
        if args.treatment_command == "enrich":
            result = enrich_data(
                main_file=args.main_file,
                lookup_file=args.lookup_file,
                main_key=args.main_key,
                lookup_key=args.lookup_key,
                columns_to_add=args.columns_to_add,
                output_file=args.output_file,
                join_how=args.join_how,
                sep=args.sep
            )
        elif args.treatment_command in ["correct_values", "replace_text"]:
            try:
                with open(args.config_file, 'r', encoding='utf-8') as f:
                    config = yaml.safe_load(f)
            except Exception as e:
                logging.error(f"Erro ao ler o arquivo de configuração {args.config_file}: {e}")
                return

            all_files = find_files(args.data_project_path, extensions=['csv', 'xlsx'])
            processed_count = 0
            for file_path in all_files:
                for rule in config.get('file_rules', []):
                    file_pattern = rule.get('file_pattern', '')
                    if re.match(file_pattern.replace('*', '.*'), os.path.basename(file_path)):
                        rules_to_apply = None
                        if args.treatment_command == "correct_values":
                            rules_to_apply = rule.get('corrections')
                            if rules_to_apply:
                                correct_values(input_file=file_path, output_file=file_path, corrections=rules_to_apply)
                        elif args.treatment_command == "replace_text":
                            rules_to_apply = rule.get('replacements')
                            if rules_to_apply:
                                replace_text(input_file=file_path, output_file=file_path, replacements=rules_to_apply)

                        if rules_to_apply:
                            processed_count += 1
                            break
            result = {"status": "success", "message": f"Operação '{args.treatment_command}' concluída. {processed_count} arquivos processados."}

        elif args.treatment_command == "remove_whitespace":
            all_files = find_files(args.data_project_path, extensions=['csv'])
            for file_path in all_files:
                remove_whitespace(input_file=file_path, output_file=file_path)
            result = {"status": "success", "message": f"Operação 'remove_whitespace' concluída. {len(all_files)} arquivos processados."}

        elif args.treatment_command == "transform_columns":
            all_files = find_files(args.data_project_path, extensions=['csv'])
            for file_path in all_files:
                try:
                    df = pd.read_csv(file_path, sep=';', keep_default_na=False, na_values=[''])
                except (pd.errors.ParserError, ValueError):
                    df = pd.read_csv(file_path, keep_default_na=False, na_values=[''])
                df_transformed = transform_columns(df)
                df_transformed.to_csv(file_path, index=False, sep=';')
            result = {"status": "success", "message": f"Operação 'transform_columns' concluída. {len(all_files)} arquivos processados."}

        elif args.treatment_command == "concatenate":
            result = concatenate_data(
                input_folder=args.data_project_path,
                output_file=args.output_file,
                file_type=args.file_type
            )

        if result:
            handle_result(result)


if __name__ == "__main__":
    main()

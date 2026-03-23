# -*- coding: utf-8 -*-

# --------------------------------------------------------------------------------
# Descrição: Wrapper fino para renomear colunas de arquivos CSV e Excel.
# Exemplo de uso:
#   python3 -m src.scripts.rename_columns --input-file ./dados.csv --old-columns A B --new-columns X Y
#
# Autor: Jules
# Criado em: 23/03/2026
# Versão: 1.0
#
# Modificado por: Jules
# Modificado em: 23/03/2026
# Licença: MIT
# --------------------------------------------------------------------------------

import argparse
import logging
from typing import Any, Dict

from src.phases.phase02_treatment.core.column_renamer import rename_columns_in_file


def setup_logging() -> None:
    """
    Configura o logging básico do wrapper.

    Returns:
        None: Esta função apenas configura o logging do processo.
    """
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )


def handle_result(result: Dict[str, Any]) -> int:
    """
    Emite a saída do wrapper e retorna o código de saída adequado.

    Args:
        result (Dict[str, Any]): Dicionário retornado pela lógica de renomeação.

    Returns:
        int: Código de saída do processo.
    """
    if result.get("message"):
        logging.info(result["message"])

    if result.get("report_path"):
        logging.info("Arquivo de saída: %s", result["report_path"])

    return 0 if result.get("status") == "success" else 1


def build_parser() -> argparse.ArgumentParser:
    """
    Monta o parser de argumentos do wrapper.

    Args:
        None: Esta função não recebe argumentos.

    Returns:
        argparse.ArgumentParser: Parser configurado para o wrapper.
    """
    parser = argparse.ArgumentParser(
        description="Renomeia colunas de arquivos CSV e Excel."
    )
    parser.add_argument("--input-file", required=True, help="Caminho para o arquivo de entrada.")
    parser.add_argument(
        "--old-columns",
        nargs="+",
        required=True,
        help="Lista de nomes atuais das colunas.",
    )
    parser.add_argument(
        "--new-columns",
        nargs="+",
        required=True,
        help="Lista de novos nomes das colunas.",
    )
    parser.add_argument(
        "--output-file",
        help="Caminho do arquivo de saída. Quando omitido, o arquivo de entrada é sobrescrito.",
    )
    parser.add_argument(
        "--delimiter",
        help="Delimitador do CSV. Quando omitido, tenta detectar automaticamente.",
    )
    parser.add_argument(
        "--sheet-name",
        help="Nome da planilha para arquivos Excel. Quando omitido, usa a primeira planilha.",
    )
    return parser


def main() -> int:
    """
    Executa o wrapper de linha de comando para renomeação de colunas.

    Args:
        None: Esta função não recebe argumentos diretamente.

    Returns:
        int: Código de saída do processo.
    """
    setup_logging()
    parser = build_parser()
    args = parser.parse_args()

    result = rename_columns_in_file(
        input_file=args.input_file,
        old_columns=args.old_columns,
        new_columns=args.new_columns,
        output_file=args.output_file,
        delimiter=args.delimiter,
        sheet_name=args.sheet_name,
    )
    return handle_result(result)


if __name__ == "__main__":
    raise SystemExit(main())

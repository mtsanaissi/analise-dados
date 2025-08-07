# -*- coding: utf-8 -*-

import argparse
import logging
import os
import sys
import json
import numpy as np

# --- Configuração Inicial do Logging ---
# Configura o logging antes de qualquer outra coisa para garantir que
# o formato e o nível sejam aplicados globalmente.
# O nível será ajustado depois de parsear os argumentos.
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    force=True)


class NpEncoder(json.JSONEncoder):
    """
    Codificador JSON personalizado para lidar com tipos de dados NumPy.
    Converte tipos NumPy em tipos nativos do Python para serialização.
    """

    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, np.floating):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return super(NpEncoder, self).default(obj)


def main():
    # --- Manual Help Handling ---
    # We check for help flags manually to allow for phase-specific help.
    is_help_request = '-h' in sys.argv or '--help' in sys.argv

    # A simple way to find the phase without full parsing.
    phase = None
    try:
        # Find the index of -p or --phase
        p_index = -1
        if '-p' in sys.argv:
            p_index = sys.argv.index('-p')
        elif '--phase' in sys.argv:
            p_index = sys.argv.index('--phase')

        if p_index != -1 and p_index + 1 < len(sys.argv):
            phase = sys.argv[p_index + 1]
    except ValueError:
        pass # No phase argument found

    # Case 1: General help request (`python src/run.py -h`)
    if is_help_request and not phase:
        # Create a temporary parser JUST to show the main help.
        main_help_parser = argparse.ArgumentParser(
            description="Orquestrador principal para as fases de análise de dados.",
            formatter_class=argparse.RawTextHelpFormatter
        )
        main_help_parser.add_argument(
            "-d", "--data-project-path", type=str, required=True,
            help="Caminho para a pasta do projeto de dados (ex: data/meu_projeto)."
        )
        main_help_parser.add_argument(
            "-p", "--phase", type=str, required=True,
            choices=['discovery', 'treatment', 'exploratory', 'visualization'],
            help="Fase a ser executada (discovery, treatment, exploratory, visualization)."
        )
        main_help_parser.print_help()
        sys.exit(0)

    # --- Main Argument Parsing ---
    # `add_help=False` prevents this parser from handling -h/--help, allowing it
    # to be passed to the phase-specific parsers.
    parser = argparse.ArgumentParser(
        description="Orquestrador principal para as fases de análise de dados.",
        formatter_class=argparse.RawTextHelpFormatter,
        add_help=False
    )

    # Arguments are not 'required' here because a phase-specific help call
    # won't have the -d argument. We'll validate manually.
    parser.add_argument("-d", "--data-project-path", type=str, help="Caminho para a pasta do projeto de dados (ex: data/meu_projeto).")
    parser.add_argument("-p", "--phase", type=str, help="Fase a ser executada (discovery, treatment, exploratory, visualization).")

    args, unknown_args = parser.parse_known_args()

    # --- Argument and Path Validation ---
    data_project_abs_path = None
    if not args.phase:
         parser.error("O argumento -p/--phase é obrigatório.")

    # Case 2: Normal execution (not a help request)
    if not is_help_request:
        if not args.data_project_path:
            parser.error("O argumento -d/--data-project-path é obrigatório para a execução da fase.")

        data_project_abs_path = os.path.abspath(os.path.expanduser(args.data_project_path))
        if not os.path.isdir(data_project_abs_path):
            logging.error(f"O caminho do projeto de dados '{data_project_abs_path}' não é um diretório válido.")
            sys.exit(1)

    # Case 3: Phase-specific help request (`python src/run.py -p discovery -h`)
    # In this case, `data_project_abs_path` remains None, which is fine for the phase orchestrators
    # as they will just show help and exit. We need to make sure '-h' is in unknown_args.
    if is_help_request and ('-h' not in unknown_args and '--help' not in unknown_args):
        unknown_args.append('-h')

    # --- Logging and Orchestration ---
    logging.getLogger().setLevel(logging.INFO)
    logging.info(f"Iniciando orquestrador para a fase: {args.phase}")
    if data_project_abs_path:
        logging.info(f"Caminho do projeto de dados: {data_project_abs_path}")

    if args.phase == 'discovery':
        from src.phases.phase01_discovery.phase01_orchestrator import run_discovery_logic
        logging.info("Executando Fase 1: Descoberta e Diagnóstico...")
        # NOTE: This is a temporary change. The main orchestrator is deprecated
        # and will be removed in a future task. We are just making it runnable
        # without extra arguments for now.
        run_discovery_logic(data_project_path=data_project_abs_path)
    elif args.phase == 'treatment':
        from src.phases.phase02_treatment.phase02_orchestrator import run_treatment_phase
        logging.info("Executando Fase 2: Tratamento e Padronização...")
        run_treatment_phase(data_project_abs_path, unknown_args)
    elif args.phase == 'exploratory':
        logging.info(
            "Executando Fase 3: Análise Exploratória e Pré-processamento...")
        # Lógica para a Fase 3
    elif args.phase == 'visualization':
        logging.info("Executando Fase 4: Visualização e Dashboards...")
        # Lógica para a Fase 4

    logging.info("Orquestração concluída.")


if __name__ == "__main__":
    main()

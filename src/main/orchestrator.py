# -*- coding: utf-8 -*-

from phases.phase01_discovery.phase01_orchestrator import run_discovery_phase
import argparse
import logging
import os
import sys
import json

# Adiciona o diretório 'src' ao sys.path para permitir importações relativas
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


def main():
    # Configuração central do logging
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(levelname)s - %(message)s')

    parser = argparse.ArgumentParser(
        description="Orquestrador principal para as fases de análise de dados.",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument(
        "-d", "--data-project-path", type=str, required=True,
        help="Caminho para a pasta do projeto de dados (ex: data/meu_projeto)."
    )
    parser.add_argument(
        "-p", "--phase", type=str, required=True,
        choices=['discovery', 'treatment', 'exploratory', 'visualization'],
        help="Fase a ser executada (discovery, treatment, exploratory, visualization)."
    )
    args = parser.parse_args()

    data_project_abs_path = os.path.abspath(
        os.path.expanduser(args.data_project_path))

    if not os.path.isdir(data_project_abs_path):
        logging.error(
            f"O caminho do projeto de dados '{data_project_abs_path}' não é um diretório válido.")
        sys.exit(1)

    logging.info(f"Iniciando orquestrador para a fase: {args.phase}")
    logging.info(f"Caminho do projeto de dados: {data_project_abs_path}")

    if args.phase == 'discovery':
        logging.info("Executando Fase 1: Descoberta e Diagnóstico...")
        results = run_discovery_phase(data_project_abs_path)

        output_filename = "discovery_report.json"
        output_path = os.path.join(data_project_abs_path, output_filename)

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=4, ensure_ascii=False)

        logging.info("\n--- Resultados da Fase 1 ---")
        logging.info(results)
    elif args.phase == 'treatment':
        logging.info("Executando Fase 2: Tratamento e Padronização...")
        # Lógica para a Fase 2
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

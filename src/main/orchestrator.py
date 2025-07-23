# -*- coding: utf-8 -*-

import argparse
import logging
import os
import sys
import json
import numpy as np

from phases.phase01_discovery.phase01_orchestrator import run_discovery_phase


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
            json.dump(results, f, indent=4,
                      ensure_ascii=False, cls=NpEncoder)

        logging.info(f"Relatório da Fase 1 salvo em: {output_path}")

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

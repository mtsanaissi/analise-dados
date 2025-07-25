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
    args, unknown_args = parser.parse_known_args()

    # Ajusta o nível de logging com base no formato de saída
    # O logging será configurado dentro de cada fase, se necessário
    logging.getLogger().setLevel(logging.INFO)

    data_project_abs_path = os.path.abspath(
        os.path.expanduser(args.data_project_path))

    if not os.path.isdir(data_project_abs_path):
        logging.error(
            f"O caminho do projeto de dados '{data_project_abs_path}' não é um diretório válido.")
        sys.exit(1)

    logging.info(f"Iniciando orquestrador para a fase: {args.phase}")
    logging.info(f"Caminho do projeto de dados: {data_project_abs_path}")

    if args.phase == 'discovery':
        from phases.phase01_discovery.phase01_orchestrator import run_discovery_phase
        logging.info("Executando Fase 1: Descoberta e Diagnóstico...")
        run_discovery_phase(data_project_abs_path, unknown_args)

    elif args.phase == 'treatment':
        from phases.phase02_treatment.phase02_orchestrator import run_treatment_phase
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

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
    parser.add_argument(
        "-o", "--output-format", type=str, default="text",
        choices=['text', 'interactive'],
        help="Formato da saída para a fase de descoberta (text, interactive)."
    )
    parser.add_argument(
        "--compare-fields",
        action="store_true",
        help="Habilita a comparação de campos/colunas entre arquivos do mesmo tipo."
    )
    args = parser.parse_args()

    # Ajusta o nível de logging com base no formato de saída
    if args.output_format == 'interactive':
        logging.getLogger().setLevel(logging.WARNING)  # Suprime INFO e DEBUG
    else:
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
        results = run_discovery_phase(
            data_project_abs_path,
            output_format=args.output_format,
            compare_fields=args.compare_fields
        )

        # A lógica de salvar o relatório JSON é mantida, pois o modo interativo
        # é um adicional que não substitui o relatório padrão.
        output_filename = "discovery_report.json"
        output_path = os.path.join(data_project_abs_path, output_filename)

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=4,
                      ensure_ascii=False, cls=NpEncoder)

        logging.info(f"Relatório da Fase 1 salvo em: {output_path}")

    elif args.phase == 'treatment':
        from phases.phase02_treatment.phase02_orchestrator import run_treatment_phase
        logging.info("Executando Fase 2: Tratamento e Padronização...")
        run_treatment_phase(data_project_abs_path)
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

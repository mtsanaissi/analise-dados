import os
import pandas as pd
from ...utils import find_files, save_df_to_csv
from ...connectors.factory import ConnectorFactory
from .core.problematic_value_extractor import extract_values
from .core.value_corrector import apply_corrections
from .core.column_transformer import transform_columns

def run_treatment_phase(data_project_path):
    """
    Orquestra a fase de tratamento dos dados.
    """
    print("--- Iniciando Fase 02: Tratamento ---")

    # Encontrar todos os arquivos de dados suportados
    supported_extensions = ["csv", "json", "xlsx"]
    files_to_process = find_files(data_project_path, supported_extensions)

    if not files_to_process:
        print("Nenhum arquivo de dados encontrado para tratamento.")
        return

    # Diretório para salvar os arquivos tratados
    treated_dir = os.path.join(data_project_path, "treated")
    os.makedirs(treated_dir, exist_ok=True)

    # Mapa de correções (exemplo, pode ser carregado de um arquivo)
    # TODO: Externalizar o mapa de correções
    corrections_map = {
        "valor_problematico_1": "valor_corrigido_1",
        "valor_problematico_2": "valor_corrigido_2"
    }

    for file_path in files_to_process:
        try:
            print(f"Processando arquivo: {os.path.basename(file_path)}")

            # 1. Carregar dados usando a fábrica de conectores
            connector = ConnectorFactory.get_connector(file_path)
            df = connector.read_data()

            if df is None:
                print(f"  -> Falha ao carregar o arquivo.")
                continue

            # 2. Extrair valores problemáticos (opcional, pode ser usado para gerar um relatório)
            problematic_values = extract_values(df)
            if problematic_values:
                print(f"  -> Valores problemáticos encontrados: {problematic_values}")

            # 3. Aplicar correções de valor
            df = apply_corrections(df, corrections_map)

            # 4. Transformar colunas (ex: remover coluna 'Total')
            df = transform_columns(df)

            # 5. Salvar o DataFrame tratado como CSV
            output_filename = os.path.splitext(os.path.basename(file_path))[0] + "_treated.csv"
            output_path = os.path.join(treated_dir, output_filename)
            save_df_to_csv(df, output_path)

            print(f"  -> Arquivo tratado salvo em: {output_path}")

        except Exception as e:
            print(f"  -> Erro ao processar o arquivo {os.path.basename(file_path)}: {e}")

    print("--- Fase 02: Tratamento Concluída ---")

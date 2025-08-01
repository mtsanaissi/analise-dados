import os
import shutil
import tempfile
import pandas as pd
import yaml
import json
from src.phases.phase02_treatment.phase02_orchestrator import run_treatment_phase
from src.utils import METADATA_DIR

def test_replace_values_with_list():
    """
    Testa a funcionalidade de substituição de valores quando 'existing_value' é uma lista.
    """
    # 1. Setup do ambiente de teste
    temp_dir = tempfile.mkdtemp()
    fad_config_dir = os.path.join(temp_dir, "fad-config")
    os.makedirs(fad_config_dir)

    try:
        # 2. Criar um DataFrame e um arquivo CSV de exemplo
        data = {
            'ID': [1, 2, 3, 4, 5, 6],
            'Status': ['Ativo', 'N/D', 'Inativo', 'NA', 'Ativo', 'Sem Info'],
            'Cidade': ['SP', 'RJ', 'N/D', 'BH', 'SP', 'NA']
        }
        df = pd.DataFrame(data)
        csv_path = os.path.join(temp_dir, "dados.csv")
        df.to_csv(csv_path, index=False, sep=';')

        # 3. Criar o arquivo de configuração YAML
        yaml_config = {
            'replacements': [
                {
                    'column': 'Status',
                    'existing_value': ['N/D', 'NA', 'Sem Info'],
                    'new_value': None  # Substituir por nulo (None se torna null no YAML)
                },
                {
                    'existing_value': 'NA', # Teste global
                    'new_value': 'Não Aplicável'
                }
            ]
        }
        yaml_path = os.path.join(fad_config_dir, "replace_rules.yaml")
        with open(yaml_path, 'w', encoding='utf-8') as f:
            yaml.dump(yaml_config, f)

        # 4. Executar a fase de tratamento
        extra_args = ["--replace-values", "replace_rules.yaml", "--report-output", "json"]
        run_treatment_phase(temp_dir, extra_args)

        # 5. Validar o arquivo CSV modificado
        df_treated = pd.read_csv(csv_path, sep=';')

        # Verificar as substituições na coluna 'Status'
        # Esperado: ['Ativo', None, 'Inativo', None, 'Ativo', None]
        # O read_csv lê None como string 'nan', então usamos isna() para verificar
        assert df_treated.loc[1, 'Status'] != df_treated.loc[1, 'Status'] # Checando se é NaN
        assert df_treated.loc[3, 'Status'] != df_treated.loc[3, 'Status']
        assert df_treated.loc[5, 'Status'] != df_treated.loc[5, 'Status']
        assert df_treated.loc[0, 'Status'] == 'Ativo'

        # Verificar a substituição global na coluna 'Cidade'
        assert df_treated.loc[5, 'Cidade'] == 'Não Aplicável'
        assert df_treated.loc[2, 'Cidade'] == 'N/D' # Não deve ser afetado pela regra global

        # 6. Validar o relatório JSON
        report_path = os.path.join(temp_dir, METADATA_DIR, "treatment_report.json")
        assert os.path.exists(report_path)

        with open(report_path, 'r') as f:
            report = json.load(f)

        assert report['summary']['total_files'] == 1
        assert report['summary']['processed_successfully'] == 1

        file_details = report['details'][0]
        assert file_details['file_name'] == 'dados.csv'
        assert file_details['status'] == 'Success'

        replacements = file_details['replacements_applied']
        assert len(replacements) == 2

        # Validar contagem da primeira regra (lista)
        rule1 = replacements[0]
        assert rule1['rule']['column'] == 'Status'
        assert rule1['count'] == 3 # 'N/D', 'NA', 'Sem Info'

        # Validar contagem da segunda regra (global)
        # A regra global 'NA' -> 'Não Aplicável' só deve afetar a coluna 'Cidade'
        # pois o 'NA' da coluna 'Status' já foi substituído pela primeira regra.
        rule2 = replacements[1]
        assert 'column' not in rule2['rule']
        assert rule2['count'] == 1 # Apenas o 'NA' em 'Cidade'

    finally:
        # 7. Limpar o ambiente de teste
        shutil.rmtree(temp_dir)


def test_replace_values_case_insensitive():
    """
    Testa a funcionalidade de substituição de valores case-insensitive.
    """
    # 1. Setup do ambiente de teste
    temp_dir = tempfile.mkdtemp()
    fad_config_dir = os.path.join(temp_dir, "fad-config")
    os.makedirs(fad_config_dir)

    try:
        # 2. Criar um DataFrame e um arquivo CSV de exemplo com variações de case
        data = {
            'ID': [1, 2, 3, 4, 5, 6],
            'Status': ['Pendente', 'pendente', 'PENDENTE', 'Finalizado', 'Pendente', 'Outro'],
            'Responsavel': ['joão', 'Maria', 'JOÃO', 'Carlos', 'pedro', 'maria']
        }
        df = pd.DataFrame(data)
        csv_path = os.path.join(temp_dir, "dados_case.csv")
        df.to_csv(csv_path, index=False, sep=';')

        # 3. Criar o arquivo de configuração YAML com regras case-sensitive e insensitive
        yaml_config = {
            'replacements': [
                {
                    'column': 'Status',
                    'existing_value': 'Pendente',
                    'new_value': 'Concluído',
                    'case_sensitive': False
                },
                {
                    'column': 'Status',
                    'existing_value': 'Finalizado',
                    'new_value': 'Encerrado',
                    'case_sensitive': True
                },
                {
                    'existing_value': 'maria',
                    'new_value': 'Maria Joaquina',
                    'case_sensitive': False
                }
            ]
        }
        yaml_path = os.path.join(fad_config_dir, "replace_rules_case.yaml")
        with open(yaml_path, 'w', encoding='utf-8') as f:
            yaml.dump(yaml_config, f)

        # 4. Executar a fase de tratamento
        extra_args = ["--replace-values", "replace_rules_case.yaml", "--report-output", "json"]
        run_treatment_phase(temp_dir, extra_args)

        # 5. Validar o arquivo CSV modificado
        df_treated = pd.read_csv(csv_path, sep=';')

        # Verificar substituições case-insensitive na coluna 'Status'
        assert df_treated.loc[0, 'Status'] == 'Concluído'
        assert df_treated.loc[1, 'Status'] == 'Concluído'
        assert df_treated.loc[2, 'Status'] == 'Concluído'
        assert df_treated.loc[4, 'Status'] == 'Concluído'

        # Verificar substituição case-sensitive na coluna 'Status'
        assert df_treated.loc[3, 'Status'] == 'Encerrado'

        # Verificar que 'Outro' não foi modificado
        assert df_treated.loc[5, 'Status'] == 'Outro'

        # Verificar substituições globais case-insensitive
        assert df_treated.loc[1, 'Responsavel'] == 'Maria Joaquina' # 'Maria'
        assert df_treated.loc[5, 'Responsavel'] == 'Maria Joaquina' # 'maria'
        assert df_treated.loc[0, 'Responsavel'] == 'joão' # Não deve ser modificado
        assert df_treated.loc[2, 'Responsavel'] == 'JOÃO' # Não deve ser modificado


        # 6. Validar o relatório JSON
        report_path = os.path.join(temp_dir, METADATA_DIR, "treatment_report.json")
        assert os.path.exists(report_path)

        with open(report_path, 'r') as f:
            report = json.load(f)

        assert report['summary']['processed_successfully'] == 1
        file_details = report['details'][0]
        assert file_details['file_name'] == 'dados_case.csv'

        replacements = file_details['replacements_applied']
        assert len(replacements) == 3

        # Validar contagens
        rule1 = next(r for r in replacements if r['rule']['existing_value'] == 'Pendente')
        rule2 = next(r for r in replacements if r['rule']['existing_value'] == 'Finalizado')
        rule3 = next(r for r in replacements if r['rule']['existing_value'] == 'maria')

        assert rule1['count'] == 4
        assert rule2['count'] == 1
        assert rule3['count'] == 2

    finally:
        # 7. Limpar o ambiente de teste
        shutil.rmtree(temp_dir)

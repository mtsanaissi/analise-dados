import os
import shutil
import pandas as pd
import yaml
import pytest
from src.phases.phase02_treatment.phase02_orchestrator import run_treatment_phase

@pytest.fixture
def temp_dir(tmpdir):
    """Cria um diretório temporário para os testes."""
    temp_data_path = tmpdir.mkdir("data")
    # Cria um subdiretório para evitar que o backup seja criado no mesmo nível
    data_subdir = temp_data_path.mkdir("project")

    # Cria o arquivo de configuração dentro do diretório do projeto
    config_dir = data_subdir.mkdir("fad-config")

    # Cria o arquivo de dados
    sample_data = {
        'ID': [1, 2, 3, 4],
        'description': ['Produto A-123', 'Produto B-456', 'Produto C-789', 'Produto A-123-extra'],
        'category': ['Eletrônicos', 'Móveis', 'Eletrônicos', 'Eletrônicos'],
        'value': [100, 200, 300, 400]
    }
    df = pd.DataFrame(sample_data)
    df.to_csv(os.path.join(data_subdir, "sample.csv"), index=False, sep=';', encoding='utf-8-sig')

    yield str(data_subdir), str(config_dir)

    shutil.rmtree(tmpdir)

def test_find_and_replace_substring(temp_dir):
    """Testa a substituição de uma substring simples."""
    data_path, config_path = temp_dir

    # Configuração YAML para o teste
    yaml_config = {
        'text_replacements': [
            {
                'column': 'description',
                'pattern': 'Produto A',
                'new_value': 'SKU-A',
                'is_regex': False
            }
        ]
    }
    config_file = os.path.join(config_path, 'replace_substring.yaml')
    with open(config_file, 'w', encoding='utf-8') as f:
        yaml.dump(yaml_config, f)

    # Executa a fase de tratamento
    run_treatment_phase(data_path, ['--find-and-replace-text', 'replace_substring.yaml'])

    # Verifica o resultado
    output_df = pd.read_csv(os.path.join(data_path, 'sample.csv'), sep=';', encoding='utf-8-sig')

    # Verifica as substituições
    assert output_df.loc[0, 'description'] == 'SKU-A-123'
    assert output_df.loc[3, 'description'] == 'SKU-A-123-extra'
    assert output_df.loc[1, 'description'] == 'Produto B-456' # Não deve ser alterado

    # Verifica o relatório
    report_path = os.path.join(data_path, 'fad-metadados', 'treatment_report.json')
    with open(report_path, 'r', encoding='utf-8') as f:
        report = yaml.safe_load(f)

    assert report['summary']['processed_successfully'] == 1
    assert report['details'][0]['replacements_applied'][0]['count'] == 2

def test_find_and_replace_regex(temp_dir):
    """Testa a substituição usando uma expressão regular."""
    data_path, config_path = temp_dir

    # Configuração YAML para o teste
    yaml_config = {
        'text_replacements': [
            {
                'column': 'description',
                'pattern': r'Produto [B-C]-\d{3}',
                'new_value': 'ITEM_REMOVED',
                'is_regex': True
            }
        ]
    }
    config_file = os.path.join(config_path, 'replace_regex.yaml')
    with open(config_file, 'w', encoding='utf-8') as f:
        yaml.dump(yaml_config, f)

    # Executa a fase de tratamento
    run_treatment_phase(data_path, ['--find-and-replace-text', 'replace_regex.yaml'])

    # Verifica o resultado
    output_df = pd.read_csv(os.path.join(data_path, 'sample.csv'), sep=';', encoding='utf-8-sig')

    # Verifica as substituições
    assert output_df.loc[1, 'description'] == 'ITEM_REMOVED'
    assert output_df.loc[2, 'description'] == 'ITEM_REMOVED'
    assert output_df.loc[0, 'description'] == 'Produto A-123' # Não deve ser alterado

    # Verifica o relatório
    report_path = os.path.join(data_path, 'fad-metadados', 'treatment_report.json')
    with open(report_path, 'r', encoding='utf-8') as f:
        report = yaml.safe_load(f)

    assert report['summary']['processed_successfully'] == 1
    assert report['details'][0]['replacements_applied'][0]['count'] == 2

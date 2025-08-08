import os
import pandas as pd
import pytest
from src.phases.phase02_treatment.core.text_replacer import replace_text

@pytest.fixture
def temp_dir(tmpdir):
    """Cria um diretório temporário para os testes."""
    data_dir = tmpdir.mkdir("data")
    sample_data = {
        'ID': [1, 2, 3, 4],
        'description': ['Produto A-123', 'Produto B-456', 'Produto C-789', 'Produto A-123-extra'],
        'category': ['Eletrônicos', 'Móveis', 'Eletrônicos', 'Eletrônicos'],
        'value': [100, 200, 300, 400]
    }
    df = pd.DataFrame(sample_data)
    input_file = data_dir.join("sample.csv")
    df.to_csv(input_file, index=False, sep=';', encoding='utf-8-sig')
    yield str(input_file), str(data_dir)

def test_find_and_replace_substring(temp_dir):
    """Testa a substituição de uma substring simples."""
    input_file, data_dir = temp_dir
    output_file = os.path.join(data_dir, "output.csv")

    replacements = [
        {
            'column': 'description',
            'pattern': 'Produto A',
            'new_value': 'SKU-A',
            'is_regex': False
        }
    ]

    result = replace_text(input_file, output_file, replacements)

    assert result['status'] == 'success'
    output_df = pd.read_csv(output_file, sep=';', encoding='utf-8-sig')
    assert output_df.loc[0, 'description'] == 'SKU-A-123'
    assert output_df.loc[3, 'description'] == 'SKU-A-123-extra'
    assert output_df.loc[1, 'description'] == 'Produto B-456'

def test_find_and_replace_regex(temp_dir):
    """Testa a substituição usando uma expressão regular."""
    input_file, data_dir = temp_dir
    output_file = os.path.join(data_dir, "output.csv")

    replacements = [
        {
            'column': 'description',
            'pattern': r'Produto [B-C]-\d{3}',
            'new_value': 'ITEM_REMOVED',
            'is_regex': True
        }
    ]

    result = replace_text(input_file, output_file, replacements)

    assert result['status'] == 'success'
    output_df = pd.read_csv(output_file, sep=';', encoding='utf-8-sig')
    assert output_df.loc[1, 'description'] == 'ITEM_REMOVED'
    assert output_df.loc[2, 'description'] == 'ITEM_REMOVED'
    assert output_df.loc[0, 'description'] == 'Produto A-123'

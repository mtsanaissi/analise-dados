import os
import pandas as pd
import pytest
from src.phases.phase02_treatment.core.whitespace_remover import remove_whitespace

def test_strip_whitespace(tmpdir):
    # Setup
    test_data_dir = str(tmpdir)

    csv_content = (
        ' "Nome"  ;"  Idade ";"  Cidade  "\n'
        ' "  João  " ;" 25 ";"  São Paulo  "\n'
        '" Maria ";"30";"Rio de Janeiro"\n'
        '"  José";" 35 ";"  Belo Horizonte  "'
    )
    input_file = os.path.join(test_data_dir, "whitespace_test.csv")
    output_file = os.path.join(test_data_dir, "whitespace_test_treated.csv")
    with open(input_file, 'w', encoding='utf-8') as f:
        f.write(csv_content)

    result = remove_whitespace(input_file, output_file)

    assert result['status'] == 'success'
    df = pd.read_csv(output_file, sep=';')

    expected_columns = ["Nome", "Idade", "Cidade"]
    assert list(df.columns) == expected_columns

    assert df['Nome'].dtype == 'object'
    assert pd.api.types.is_integer_dtype(df['Idade']), f"A coluna 'Idade' deveria ser numérica, mas é {df['Idade'].dtype}"
    assert df['Cidade'].dtype == 'object'

    assert df.iloc[0, 0] == "João"
    assert df.iloc[0, 1] == 25
    assert df.iloc[0, 2] == "São Paulo"
    assert df.iloc[1, 0] == "Maria"
    assert df.iloc[1, 1] == 30
    assert df.iloc[2, 2] == "Belo Horizonte"
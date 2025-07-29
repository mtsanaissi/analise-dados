# -*- coding: utf-8 -*-
import pandas as pd
import pytest
from src.phases.phase03_exploratory.p3_03_transform_denormalize_rows import denormalize_rows

def test_denormalize_rows(tmp_path):
    # Criar arquivo Excel de amostra
    input_file = tmp_path / "input.xlsx"
    output_file = tmp_path / "output.xlsx"

    sample_data = {
        "Id Recomendação": [1, 2, 3],
        "Categorias": ["Categoria A\nCategoria B", "Categoria C", "Categoria D\n\nCategoria E"]
    }
    df = pd.DataFrame(sample_data)
    df.to_excel(input_file, index=False)

    # Chamar a função
    denormalize_rows(str(input_file), str(output_file))

    # Verificar o arquivo de saída
    assert output_file.exists()

    # Ler e verificar o conteúdo do arquivo de saída
    df_output = pd.read_excel(output_file)

    expected_data = {
        "Id Recomendação": [1, 1, 2, 3, 3],
        "Categorias": ["Categoria A", "Categoria B", "Categoria C", "Categoria D", "Categoria E"]
    }
    df_expected = pd.DataFrame(expected_data)

    pd.testing.assert_frame_equal(df_output, df_expected)

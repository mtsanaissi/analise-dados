# -*- coding: utf-8 -*-
import pandas as pd
import pytest
from src.phases.phase03_exploratory.p3_02_preprocess_filter_batch import preprocess_filter_batch

def test_preprocess_filter_batch(tmp_path):
    # Criar diretórios de entrada e saída
    input_dir = tmp_path / "input"
    input_dir.mkdir()
    output_dir = tmp_path / "output"
    output_dir.mkdir()

    # Criar arquivo CSV de amostra
    sample_data = {
        "Segmento de Mercado": [
            "Operadoras de Telecomunicações (Telefonia, Internet, TV por assinatura)",
            "Bancos, Financeiras e Administradoras de Cartão",
            "Energia Elétrica",
            "Transporte Aéreo"
        ],
        "Tempo Resposta": [10, 5, -2, 15]
    }
    df = pd.DataFrame(sample_data)
    csv_path = input_dir / "sample.csv"
    df.to_csv(csv_path, index=False, sep=";")

    # Chamar a função
    preprocess_filter_batch(
        root_directory=str(input_dir),
        output_directory=str(output_dir),
        extensions=["csv"],
        recursive=True,
        delimiter=";"
    )

    # Verificar o arquivo de saída
    output_csv_path = output_dir / "sample.csv"
    assert output_csv_path.exists()

    # Ler e verificar o conteúdo do arquivo de saída
    df_output = pd.read_csv(output_csv_path, sep=";")
    assert len(df_output) == 2
    assert "Operadoras de Telecomunicações (Telefonia, Internet, TV por assinatura)" in df_output["Segmento de Mercado"].values
    assert "Transporte Aéreo" in df_output["Segmento de Mercado"].values
    assert "Bancos, Financeiras e Administradoras de Cartão" not in df_output["Segmento de Mercado"].values
    assert all(df_output["Tempo Resposta"] >= 0)

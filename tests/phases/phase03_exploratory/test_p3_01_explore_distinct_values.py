# -*- coding: utf-8 -*-
import pandas as pd
import pytest
from src.phases.phase03_exploratory.p3_01_explore_distinct_values import explore_distinct_values

def test_explore_distinct_values(tmp_path, capsys):
    # Criar diretório de dados de teste
    data_dir = tmp_path / "data"
    data_dir.mkdir()

    # Criar arquivo CSV de amostra
    sample_data = {
        "coluna_a": ["A", "B", "A", "C"],
        "coluna_b": [1, 2, 1, 3],
        "coluna_c": ["X", "Y", "X", "Z"]
    }
    df = pd.DataFrame(sample_data)
    csv_path = data_dir / "sample.csv"
    df.to_csv(csv_path, index=False, sep=";")

    # Chamar a função e capturar a saída
    explore_distinct_values(
        root_directory=str(data_dir),
        columns=["coluna_a", "coluna_b"],
        extensions=["csv"],
        recursive=True,
        delimiter=";"
    )

    # Verificar a saída
    captured = capsys.readouterr()
    assert "--- Coluna: 'coluna_a' ---" in captured.out
    assert "- A" in captured.out
    assert "- B" in captured.out
    assert "- C" in captured.out
    assert "Total de valores distintos encontrados: 3" in captured.out

    assert "--- Coluna: 'coluna_b' ---" in captured.out
    assert "- 1" in captured.out
    assert "- 2" in captured.out
    assert "- 3" in captured.out
    assert "Total de valores distintos encontrados: 3" in captured.out

    assert "coluna_c" not in captured.out

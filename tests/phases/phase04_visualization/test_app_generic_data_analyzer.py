import pandas as pd
import pytest
from src.phases.phase04_visualization.app_generic_data_analyzer import load_data, get_data_summary

def test_load_data_csv(tmp_path):
    # Criar um arquivo CSV de exemplo
    data = {'col1': [1, 2], 'col2': ['A', 'B']}
    df = pd.DataFrame(data)
    csv_path = tmp_path / "test.csv"
    df.to_csv(csv_path, index=False, sep=';')

    # Testar o carregamento do CSV
    loaded_df = load_data(str(csv_path), delimiter=';')
    assert isinstance(loaded_df, pd.DataFrame)
    assert loaded_df.equals(df)

def test_load_data_excel(tmp_path):
    # Criar um arquivo Excel de exemplo
    data = {'col1': [1.1, 2.2], 'col2': [True, False]}
    df = pd.DataFrame(data)
    excel_path = tmp_path / "test.xlsx"
    df.to_excel(excel_path, index=False)

    # Testar o carregamento do Excel
    loaded_df = load_data(str(excel_path))
    assert isinstance(loaded_df, pd.DataFrame)
    assert loaded_df.equals(df)

def test_load_data_unsupported_format(tmp_path):
    # Testar o carregamento de um formato não suportado
    unsupported_file = tmp_path / "test.txt"
    unsupported_file.write_text("dummy content")
    with pytest.raises(ValueError, match="Formato de arquivo não suportado"):
        load_data(str(unsupported_file))

def test_get_data_summary():
    # Criar um DataFrame de exemplo
    data = {'numeric': [1, 2, 3], 'text': ['A', 'B', 'A']}
    df = pd.DataFrame(data)

    # Obter o resumo dos dados
    summary = get_data_summary(df)

    # Verificar se o resumo foi gerado corretamente
    assert isinstance(summary, pd.DataFrame)
    assert 'numeric' in summary.columns
    assert 'text' in summary.columns
    assert summary.loc['count', 'numeric'] == 3
    assert summary.loc['top', 'text'] == 'A'
    assert summary.loc['freq', 'text'] == 2

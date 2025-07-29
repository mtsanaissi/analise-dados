import pandas as pd
from src.phases.phase04_visualization.app_explore_single_profile import load_dataframe

def test_load_dataframe_csv(tmp_path):
    # Criar um arquivo CSV de exemplo
    data = {'col1': [1, 2], 'col2': ['A', 'B']}
    df = pd.DataFrame(data)
    csv_path = tmp_path / "test.csv"
    df.to_csv(csv_path, index=False, sep=';')

    # Testar o carregamento do CSV
    loaded_df = load_dataframe(str(csv_path), delimiter=';')
    assert isinstance(loaded_df, pd.DataFrame)
    assert loaded_df.equals(df)

def test_load_dataframe_excel(tmp_path):
    # Criar um arquivo Excel de exemplo
    data = {'col1': [1.1, 2.2], 'col2': [True, False]}
    df = pd.DataFrame(data)
    excel_path = tmp_path / "test.xlsx"
    df.to_excel(excel_path, index=False)

    # Testar o carregamento do Excel
    loaded_df = load_dataframe(str(excel_path), delimiter=None)
    assert isinstance(loaded_df, pd.DataFrame)
    assert loaded_df.equals(df)

def test_load_dataframe_unsupported_file(tmp_path):
    # Criar um arquivo com extensão não suportada
    unsupported_file = tmp_path / "test.txt"
    unsupported_file.write_text("dummy content")

    # Testar o carregamento de um arquivo não suportado
    loaded_df = load_dataframe(str(unsupported_file), delimiter=None)
    assert loaded_df is None

def test_load_dataframe_nonexistent_file():
    # Testar o carregamento de um arquivo que não existe
    loaded_df = load_dataframe("nonexistent_file.csv", delimiter=',')
    assert loaded_df is None

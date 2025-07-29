import os
import pandas as pd
from src.phases.phase04_visualization.app_explore_aggregated_profiles import (
    find_and_parse_files,
    filter_files_by_year,
    load_and_concat_data,
)

def test_find_and_parse_files(tmp_path):
    # Criar arquivos de teste com anos nos nomes
    (tmp_path / "data-2023-01.csv").touch()
    (tmp_path / "data-2023-02.csv").touch()
    (tmp_path / "data-2024-01.csv").touch()
    (tmp_path / "no_date_file.csv").touch()

    parsed_files = find_and_parse_files(str(tmp_path), recursive=False)

    assert len(parsed_files) == 3
    years = [year for path, year in parsed_files]
    assert 2023 in years
    assert 2024 in years
    assert all(isinstance(year, int) for year in years)

def test_filter_files_by_year():
    parsed_files = [
        ("path/data-2023-01.csv", 2023),
        ("path/data-2023-02.csv", 2023),
        ("path/data-2024-01.csv", 2024),
    ]

    filtered_2023 = filter_files_by_year(parsed_files, 2023)
    assert len(filtered_2023) == 2
    assert all("2023" in path for path in filtered_2023)

    filtered_2024 = filter_files_by_year(parsed_files, 2024)
    assert len(filtered_2024) == 1
    assert "2024" in filtered_2024[0]

def test_load_and_concat_data(tmp_path):
    # Criar arquivos CSV de exemplo
    df1 = pd.DataFrame({'a': [1], 'b': [2]})
    df2 = pd.DataFrame({'a': [3], 'b': [4]})
    path1 = tmp_path / "file1.csv"
    path2 = tmp_path / "file2.csv"
    df1.to_csv(path1, index=False)
    df2.to_csv(path2, index=False)

    concatenated_df = load_and_concat_data([str(path1), str(path2)], delimiter=',')

    assert not concatenated_df.empty
    assert len(concatenated_df) == 2
    assert list(concatenated_df.columns) == ['a', 'b']
    assert concatenated_df.iloc[1]['a'] == 3

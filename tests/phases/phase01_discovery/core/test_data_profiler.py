import pandas as pd
import pytest
from src.phases.phase01_discovery.core.data_profiler import profile_dataframe

def test_profile_dataframe_numeric():
    data = {'col1': [1, 2, 3, 4, 5]}
    df = pd.DataFrame(data)
    profile = profile_dataframe(df)
    assert profile[0]['tipo_inferido'] == 'Numérico'
    assert profile[0]['estatisticas']['media'] == 3.0

def test_profile_dataframe_datetime():
    data = {'col1': ['2021-01-01', '2021-01-02', '2021-01-03']}
    df = pd.DataFrame(data)
    profile = profile_dataframe(df)
    assert profile[0]['tipo_inferido'] == 'Data/Hora'

def test_profile_dataframe_categorical():
    data = {'col1': ['A', 'B', 'A', 'C', 'B']}
    df = pd.DataFrame(data)
    profile = profile_dataframe(df)
    assert profile[0]['tipo_inferido'] == 'Categórico/Texto'
    assert profile[0]['estatisticas']['valores_unicos'] == 3

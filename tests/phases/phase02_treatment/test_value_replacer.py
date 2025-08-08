import os
import tempfile
import pandas as pd
import yaml
import pytest
from src.phases.phase02_treatment.core.value_corrector import correct_values
import numpy as np

def test_replace_values_with_list(tmpdir):
    """
    Testa a funcionalidade de substituição de valores quando 'existing_value' é uma lista.
    """
    temp_dir = str(tmpdir)
    input_file = os.path.join(temp_dir, "dados.csv")
    output_file = os.path.join(temp_dir, "dados_tratados.csv")
    data = {
        'ID': [1, 2, 3, 4, 5, 6],
        'Status': ['Ativo', 'N/D', 'Inativo', 'NA', 'Ativo', 'Sem Info'],
        'Cidade': ['SP', 'RJ', 'N/D', 'BH', 'SP', 'NA']
    }
    df = pd.DataFrame(data)
    df.to_csv(input_file, index=False, sep=';')

    replacements = [
        {
            'column': 'Status',
            'existing_value': ['N/D', 'NA', 'Sem Info'],
            'new_value': np.nan
        },
        {
            'column': 'Cidade',
            'existing_value': 'NA',
            'new_value': 'Não Aplicável'
        }
    ]

    result = correct_values(input_file, output_file, replacements)

    assert result['status'] == 'success'
    df_treated = pd.read_csv(output_file, sep=';')
    assert pd.isna(df_treated.loc[1, 'Status'])
    assert pd.isna(df_treated.loc[3, 'Status'])
    assert pd.isna(df_treated.loc[5, 'Status'])
    assert df_treated.loc[0, 'Status'] == 'Ativo'
    assert df_treated.loc[5, 'Cidade'] == 'Não Aplicável'
    assert df_treated.loc[2, 'Cidade'] == 'N/D'

def test_replace_values_case_insensitive(tmpdir):
    """
    Testa a funcionalidade de substituição de valores case-insensitive.
    """
    temp_dir = str(tmpdir)
    input_file = os.path.join(temp_dir, "dados_case.csv")
    output_file = os.path.join(temp_dir, "dados_case_tratados.csv")
    data = {
        'ID': [1, 2, 3, 4, 5, 6],
        'Status': ['Pendente', 'pendente', 'PENDENTE', 'Finalizado', 'Pendente', 'Outro'],
        'Responsavel': ['joão', 'Maria', 'JOÃO', 'Carlos', 'pedro', 'maria']
    }
    df = pd.DataFrame(data)
    df.to_csv(input_file, index=False, sep=';')

    replacements = [
        {
            'column': 'Status',
            'existing_value': 'Pendente',
            'new_value': 'Concluído',
            'case_sensitive': False
        },
        {
            'column': 'Status',
            'existing_value': 'Finalizado',
            'new_value': 'Encerrado',
            'case_sensitive': True
        },
        {
            'existing_value': 'maria',
            'new_value': 'Maria Joaquina',
            'case_sensitive': False
        }
    ]

    result = correct_values(input_file, output_file, replacements)

    assert result['status'] == 'success'
    df_treated = pd.read_csv(output_file, sep=';')
    assert df_treated.loc[0, 'Status'] == 'Concluído'
    assert df_treated.loc[1, 'Status'] == 'Concluído'
    assert df_treated.loc[2, 'Status'] == 'Concluído'
    assert df_treated.loc[4, 'Status'] == 'Concluído'
    assert df_treated.loc[3, 'Status'] == 'Encerrado'
    assert df_treated.loc[5, 'Status'] == 'Outro'
    assert df_treated.loc[1, 'Responsavel'] == 'Maria Joaquina'
    assert df_treated.loc[5, 'Responsavel'] == 'Maria Joaquina'
    assert df_treated.loc[0, 'Responsavel'] == 'joão'
    assert df_treated.loc[2, 'Responsavel'] == 'JOÃO'

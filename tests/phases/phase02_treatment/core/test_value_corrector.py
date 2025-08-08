import pandas as pd
import numpy as np
import pytest
from src.phases.phase02_treatment.core.value_corrector import correct_values

def test_correct_values_to_nan(tmp_path):
    # Arrange
    input_file = tmp_path / "input.csv"
    output_file = tmp_path / "output.csv"
    data = {'A': [1, 2, -1], 'B': [3, -99, 5]}
    df = pd.DataFrame(data)
    df.to_csv(input_file, index=False, sep=';')
    corrections = [
        {'existing_value': -1, 'new_value': np.nan},
        {'existing_value': -99, 'new_value': np.nan}
    ]

    # Act
    result = correct_values(str(input_file), str(output_file), corrections)

    # Assert
    assert result['status'] == 'success'
    assert result['report_path'] == str(output_file)
    corrected_df = pd.read_csv(output_file, sep=';')
    assert pd.isna(corrected_df.loc[2, 'A'])
    assert pd.isna(corrected_df.loc[1, 'B'])

def test_correct_values_to_zero(tmp_path):
    # Arrange
    input_file = tmp_path / "input.csv"
    output_file = tmp_path / "output.csv"
    data = {'A': [1, 2, -1], 'B': [3, -99, 5]}
    df = pd.DataFrame(data)
    df.to_csv(input_file, index=False, sep=';')
    corrections = [
        {'existing_value': -1, 'new_value': 0},
        {'existing_value': -99, 'new_value': 0}
    ]

    # Act
    result = correct_values(str(input_file), str(output_file), corrections)

    # Assert
    assert result['status'] == 'success'
    corrected_df = pd.read_csv(output_file, sep=';')
    assert corrected_df.loc[2, 'A'] == 0
    assert corrected_df.loc[1, 'B'] == 0

import pandas as pd
import numpy as np
from src.phases.phase02_treatment.core.value_corrector import apply_corrections

def test_correct_values_to_nan():
    # Arrange
    data = {'A': [1, 2, -1], 'B': [3, -99, 5]}
    df = pd.DataFrame(data)
    corrections_map = {-1: np.nan, -99: np.nan}

    # Act
    corrected_df = apply_corrections(df, corrections_map)

    # Assert
    assert pd.isna(corrected_df.loc[2, 'A'])
    assert pd.isna(corrected_df.loc[1, 'B'])

def test_correct_values_to_zero():
    # Arrange
    data = {'A': [1, 2, -1], 'B': [3, -99, 5]}
    df = pd.DataFrame(data)
    corrections_map = {-1: 0, -99: 0}

    # Act
    corrected_df = apply_corrections(df, corrections_map)

    # Assert
    assert corrected_df.loc[2, 'A'] == 0
    assert corrected_df.loc[1, 'B'] == 0

import pandas as pd
from src.phases.phase02_treatment.core.problematic_value_extractor import extract_values

def test_extract_problematic_values():
    # Arrange
    data = {'Cidade': ['São Paulo', 'Rio de Janeiro', 'Belo Horizonte¬'], 'UF': ['SP', 'RJ', 'MG']}
    df = pd.DataFrame(data)

    # Act
    problematic_values = extract_values(df)

    # Assert
    assert problematic_values is not None
    assert 'Cidade' in problematic_values
    assert 'Belo Horizonte¬ - MG' in problematic_values['Cidade']

def test_extract_problematic_values_with_no_problematic_values():
    # Arrange
    data = {'A': ['a', 'b', 'c'], 'B': ['d', 'e', 'f']}
    df = pd.DataFrame(data)

    # Act
    problematic_values = extract_values(df)

    # Assert
    assert problematic_values is None

import pandas as pd
from src.phases.phase02_treatment.core.column_transformer import transform_columns

def test_rename_columns():
    # Arrange
    data = {'A': [1, 2], 'B': [3, 4], 'Total': [4, 6]}
    df = pd.DataFrame(data)

    # Act
    transformed_df = transform_columns(df)

    # Assert
    assert 'Total' not in transformed_df.columns
    assert 'A' in transformed_df.columns
    assert 'B' in transformed_df.columns

def test_rename_columns_with_no_total_column():
    # Arrange
    data = {'A': [1, 2], 'B': [3, 4]}
    df = pd.DataFrame(data)

    # Act
    transformed_df = transform_columns(df)

    # Assert
    assert 'A' in transformed_df.columns
    assert 'B' in transformed_df.columns
    assert df.equals(transformed_df)

def test_transform_column_type_to_string():
    # Arrange
    data = {'OutraColuna': [1, 2], 'Dep_Time': [800, 1230]}
    df = pd.DataFrame(data)

    # Act
    transformed_df = transform_columns(df)

    # Assert
    assert transformed_df['Dep_Time'].dtype == object
    assert transformed_df['Dep_Time'][0] == '0800'
    assert transformed_df['Dep_Time'][1] == '1230'

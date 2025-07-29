import pandas as pd
import os
from src.phases.phase02_treatment.core.data_concatenator import DataConcatenator

def test_concatenate_data(tmp_path):
    # Arrange
    input_folder = tmp_path / "input"
    output_file = tmp_path / "output.csv"
    input_folder.mkdir()

    df1 = pd.DataFrame({'A': [1, 2], 'B': [3, 4]})
    df2 = pd.DataFrame({'A': [5, 6], 'B': [7, 8]})

    df1.to_csv(input_folder / "file1.csv", index=False)
    df2.to_csv(input_folder / "file2.csv", index=False)

    config = {
        'input_folder': str(input_folder),
        'output_file': str(output_file),
        'file_type': 'csv'
    }

    # Act
    concatenator = DataConcatenator(config)
    concatenator.concatenate_files()

    # Assert
    assert os.path.exists(output_file)
    concatenated_df = pd.read_csv(output_file).sort_values(by='A').reset_index(drop=True)
    expected_df = pd.DataFrame({'A': [1, 2, 5, 6], 'B': [3, 4, 7, 8]}).sort_values(by='A').reset_index(drop=True)
    pd.testing.assert_frame_equal(concatenated_df, expected_df)

def test_concatenate_data_with_no_files(tmp_path):
    # Arrange
    input_folder = tmp_path / "input"
    output_file = tmp_path / "output.csv"
    input_folder.mkdir()

    config = {
        'input_folder': str(input_folder),
        'output_file': str(output_file),
        'file_type': 'csv'
    }

    # Act
    concatenator = DataConcatenator(config)
    concatenator.concatenate_files()

    # Assert
    assert not os.path.exists(output_file)

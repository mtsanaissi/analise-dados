import pytest
import json
import pandas as pd
from unittest.mock import patch, MagicMock, ANY
from src.phases.phase02_treatment.phase02_orchestrator import run_treatment_phase

@patch('src.phases.phase02_treatment.phase02_orchestrator.DataEnricher')
def test_orchestrator_enrich_data_routing(mock_data_enricher, tmp_path):
    # Arrange
    config = {
        'main_file': 'main.csv',
        'lookup_file': 'lookup.csv',
        'main_key': 'key',
        'lookup_key': 'key',
        'columns_to_add': ['extra_data'],
        'output_file': 'output.csv'
    }
    config_path = tmp_path / "enrich_config.json"
    with open(config_path, 'w') as f:
        json.dump(config, f)

    args = ['--enrich-data', str(config_path)]

    # Act
    run_treatment_phase(str(tmp_path), args)

    # Assert
    mock_data_enricher.assert_called_once()
    mock_data_enricher.return_value.enrich_data.assert_called_once()

@patch('src.phases.phase02_treatment.phase02_orchestrator.DataConcatenator')
def test_orchestrator_concatenate_data_routing(mock_data_concatenator, tmp_path):
    # Arrange
    config = {
        'input_folder': 'data/',
        'output_file': 'output.csv',
        'file_type': 'csv'
    }
    config_path = tmp_path / "concat_config.json"
    with open(config_path, 'w') as f:
        json.dump(config, f)

    args = ['--concatenate-data', str(config_path)]

    # Act
    run_treatment_phase(str(tmp_path), args)

    # Assert
    mock_data_concatenator.assert_called_once()
    mock_data_concatenator.return_value.concatenate_files.assert_called_once()

@patch('src.phases.phase02_treatment.phase02_orchestrator.shutil.move')
@patch('src.phases.phase02_treatment.phase02_orchestrator.find_files')
@patch('src.phases.phase02_treatment.phase02_orchestrator.get_data_loader')
@patch('src.phases.phase02_treatment.phase02_orchestrator.extract_values')
@patch('src.phases.phase02_treatment.phase02_orchestrator.apply_corrections')
@patch('src.phases.phase02_treatment.phase02_orchestrator.transform_columns')
def test_orchestrator_default_routing(mock_transform, mock_apply, mock_extract, mock_get_loader, mock_find_files, mock_shutil_move, tmp_path):
    # Arrange
    dummy_file = tmp_path / "file1.csv"
    dummy_file.touch()
    mock_find_files.return_value = [str(dummy_file)]

    # Mock the chain of DataFrame transformations
    mock_df_initial = MagicMock(spec=pd.DataFrame)
    mock_df_after_corrections = MagicMock(spec=pd.DataFrame)
    mock_df_after_transform = MagicMock(spec=pd.DataFrame)

    mock_get_loader.return_value.read.return_value = mock_df_initial
    mock_apply.return_value = mock_df_after_corrections
    mock_transform.return_value = mock_df_after_transform
    args = ['--apply-standard-treatment']

    # Act
    run_treatment_phase(str(tmp_path), args)

    # Assert
    mock_find_files.assert_called_once()
    mock_get_loader.assert_called_with(str(dummy_file))
    mock_extract.assert_called_with(mock_df_initial)
    mock_apply.assert_called_with(mock_df_initial, ANY)
    mock_transform.assert_called_with(mock_df_after_corrections)
    mock_shutil_move.assert_called_once()
    mock_df_after_transform.to_csv.assert_called_with(str(dummy_file), index=False, sep=';', encoding='utf-8-sig')

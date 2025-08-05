import pytest
import yaml
import json
import pandas as pd
from unittest.mock import patch, MagicMock, ANY
from src.phases.phase02_treatment.phase02_orchestrator import run_treatment_phase

@patch('src.phases.phase02_treatment.phase02_orchestrator.DataEnricher')
def test_orchestrator_enrich_data_routing(mock_data_enricher, tmp_path):
    # Arrange
    config_dir = tmp_path / "fad-config"
    config_dir.mkdir()
    config_path = config_dir / "enrich_config.yaml"
    config = {
        'main_file': 'main.csv',
        'lookup_file': 'lookup.csv',
        'main_key': 'key',
        'lookup_key': 'key',
        'columns_to_add': ['extra_data'],
        'output_file': 'output.csv'
    }
    with open(config_path, 'w') as f:
        yaml.dump(config, f)

    args = ['--enrich-data', str(config_path)]

    # Act
    run_treatment_phase(str(tmp_path), args)

    # Assert
    mock_data_enricher.assert_called_once_with(config, str(tmp_path))
    mock_data_enricher.return_value.enrich_data.assert_called_once()

@patch('src.phases.phase02_treatment.phase02_orchestrator.DataEnricher')
def test_orchestrator_enrich_data_routing_absolute_path(mock_data_enricher, tmp_path):
    # Arrange
    config = {
        'main_file': 'main.csv',
        'lookup_file': 'lookup.csv',
        'main_key': 'key',
        'lookup_key': 'key',
        'columns_to_add': ['extra_data'],
        'output_file': 'output.csv'
    }
    config_path = tmp_path / "enrich_config.yaml"
    with open(config_path, 'w') as f:
        yaml.dump(config, f)

    args = ['--enrich-data', str(config_path)]

    # Act
    run_treatment_phase(str(tmp_path), args)

    # Assert
    mock_data_enricher.assert_called_once()
    mock_data_enricher.return_value.enrich_data.assert_called_once()

@patch('src.phases.phase02_treatment.phase02_orchestrator.DataConcatenator')
def test_orchestrator_concatenate_data_routing(mock_data_concatenator, tmp_path):
    # Arrange
    config_dir = tmp_path / "fad-config"
    config_dir.mkdir()
    config_path = config_dir / "concat_config.yaml"
    config = {
        'input_folder': 'data/',
        'output_file': 'output.csv',
        'file_type': 'csv'
    }
    with open(config_path, 'w') as f:
        yaml.dump(config, f)

    args = ['--concatenate-data', 'concat_config.yaml']

    # Act
    run_treatment_phase(str(tmp_path), args)

    # Assert
    mock_data_concatenator.assert_called_once()
    mock_data_concatenator.return_value.concatenate_files.assert_called_once()

@patch('src.phases.phase02_treatment.phase02_orchestrator.shutil.move')
@patch('src.phases.phase02_treatment.phase02_orchestrator.find_files')
@patch('src.phases.phase02_treatment.phase02_orchestrator.get_data_loader')
def test_orchestrator_replace_values_routing(mock_get_loader, mock_find_files, mock_shutil_move, tmp_path):
    # Arrange
    # Setup paths
    config_dir = tmp_path / "fad-config"
    config_dir.mkdir()
    dummy_file = tmp_path / "file1.csv"
    config_path = config_dir / "replace_config.yaml"

    # Create dummy data and config
    input_df = pd.DataFrame({
        'Status': ['Old', 'Active', 'Old'],
        'Data': [1, 2, 'N/A']
    })
    input_df.to_csv(dummy_file, index=False, sep=';')

    config = {
        'replacements': [
            {'column': 'Status', 'existing_value': 'Old', 'new_value': 'New'},
            {'existing_value': 'N/A', 'new_value': None}
        ]
    }
    with open(config_path, 'w') as f:
        yaml.dump(config, f)

    # Mock the components that interact with the file system or external libraries
    mock_find_files.return_value = [str(dummy_file)]
    mock_get_loader.return_value.read.return_value = pd.read_csv(dummy_file, sep=';')


    args = ['--replace-values', 'replace_config.yaml', '--report-output', 'json']

    # Act
    run_treatment_phase(str(tmp_path), args)

    # Assert
    mock_find_files.assert_called_once()
    mock_shutil_move.assert_called_once()

    # Read the modified file and verify its contents
    result_df = pd.read_csv(dummy_file, sep=';')
    expected_df = pd.DataFrame({
        'Status': ['New', 'Active', 'New'],
        'Data': [1.0, 2.0, pd.NA]
    }).astype({'Data': 'object'})
    # Convert 'N/A' to NaN, then to object to match pandas behavior
    result_df['Data'] = pd.to_numeric(result_df['Data'], errors='coerce')
    expected_df['Data'] = pd.to_numeric(expected_df['Data'], errors='coerce')

    # Fill NA/NaN with a placeholder for comparison
    pd.testing.assert_frame_equal(
        result_df.fillna(-1),
        expected_df.fillna(-1)
    )

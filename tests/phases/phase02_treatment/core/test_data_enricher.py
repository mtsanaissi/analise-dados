import pandas as pd
import pytest
from src.phases.phase02_treatment.core.data_enricher import enrich_data

def test_enrich_data_success(tmp_path):
    # Arrange
    main_file = tmp_path / "main.csv"
    lookup_file = tmp_path / "lookup.csv"
    output_file = tmp_path / "output.csv"

    main_data = {'key': ['A', 'B', 'C'], 'value': [1, 2, 3]}
    lookup_data = {'key': ['A', 'B', 'C'], 'extra_data': [4, 5, 6]}

    main_df = pd.DataFrame(main_data)
    lookup_df = pd.DataFrame(lookup_data)

    main_df.to_csv(main_file, index=False)
    lookup_df.to_csv(lookup_file, index=False)

    # Act
    result = enrich_data(
        main_file=str(main_file),
        lookup_file=str(lookup_file),
        main_key='key',
        lookup_key='key',
        columns_to_add=['extra_data'],
        output_file=str(output_file)
    )

    # Assert
    assert result['status'] == 'success'
    assert result['report_path'] == str(output_file)
    enriched_df = pd.read_csv(output_file)
    assert 'extra_data' in enriched_df.columns
    assert len(enriched_df) == 3
    assert enriched_df['extra_data'].tolist() == [4, 5, 6]

def test_enrich_data_duplicate_keys_in_lookup(tmp_path):
    # Arrange
    main_file = tmp_path / "main.csv"
    lookup_file = tmp_path / "lookup.csv"
    output_file = tmp_path / "output.csv"

    main_data = {'key': ['A', 'B', 'C'], 'value': [1, 2, 3]}
    lookup_data = {'key': ['A', 'A', 'C'], 'extra_data': [4, 5, 6]}

    main_df = pd.DataFrame(main_data)
    lookup_df = pd.DataFrame(lookup_data)

    main_df.to_csv(main_file, index=False)
    lookup_df.to_csv(lookup_file, index=False)

    # Act
    result = enrich_data(
        main_file=str(main_file),
        lookup_file=str(lookup_file),
        main_key='key',
        lookup_key='key',
        columns_to_add=['extra_data'],
        output_file=str(output_file)
    )

    # Assert
    assert result['status'] == 'success'
    enriched_df = pd.read_csv(output_file)
    assert 'extra_data' in enriched_df.columns
    assert pd.isna(enriched_df.loc[0, 'extra_data'])

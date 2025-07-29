# -*- coding: utf-8 -*-
import pandas as pd
import pytest
from src.connectors.csv_connector import CsvConnector

def test_csv_connector_read(tmp_path):
    """Testa o método read da classe CsvConnector."""
    # Arrange
    p = tmp_path / "test.csv"
    p.write_text("a,b\n1,2")
    connector = CsvConnector(str(p), delimiter=',')

    # Act
    df = connector.read()

    # Assert
    assert isinstance(df, pd.DataFrame)
    assert df.columns.tolist() == ["a", "b"]
    assert df.iloc[0, 0] == 1

def test_csv_connector_write(tmp_path):
    """Testa o método write da classe CsvConnector."""
    # Arrange
    df = pd.DataFrame({"a": [1], "b": [2]})
    p = tmp_path / "output.csv"
    connector = CsvConnector(str(p), delimiter=',')

    # Act
    connector.write(df)

    # Assert
    assert p.exists()
    read_df = pd.read_csv(p, sep=',')
    pd.testing.assert_frame_equal(df, read_df)

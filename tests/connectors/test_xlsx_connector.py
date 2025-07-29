import pandas as pd
import pytest
from src.connectors.xlsx_connector import XlsxConnector

def test_read_xlsx_single_sheet(tmp_path):
    """
    Testa se o XlsxConnector lê corretamente a primeira planilha de um arquivo Excel
    com múltiplas planilhas.
    """
    # Arrange
    file_path = tmp_path / "test.xlsx"
    df1 = pd.DataFrame({'col1': [1, 2], 'col2': [3, 4]})
    df2 = pd.DataFrame({'colA': ['A', 'B'], 'colB': ['C', 'D']})

    with pd.ExcelWriter(file_path) as writer:
        df1.to_excel(writer, sheet_name='Primeira Planilha', index=False)
        df2.to_excel(writer, sheet_name='Segunda Planilha', index=False)

    connector = XlsxConnector(str(file_path))

    # Act
    result_df = connector.read()

    # Assert
    assert isinstance(result_df, pd.DataFrame)
    pd.testing.assert_frame_equal(result_df, df1)

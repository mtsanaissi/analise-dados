# -*- coding: utf-8 -*-
import pytest
from src.connectors.factory import get_data_loader
from src.connectors.csv_connector import CsvConnector

def test_get_data_loader_csv():
    """Testa se get_data_loader retorna CsvConnector para arquivos .csv."""
    # Act
    loader = get_data_loader("test.csv")

    # Assert
    assert isinstance(loader, CsvConnector)

def test_get_data_loader_unsupported_extension():
    """Testa se get_data_loader levanta um ValueError para extensões não suportadas."""
    # Act & Assert
    with pytest.raises(ValueError, match="Extensão de arquivo não suportada"):
        get_data_loader("test.txt")

def test_get_data_loader_json():
    """Testa se get_data_loader levanta um ValueError para .json (ainda não implementado)."""
    with pytest.raises(ValueError):
        get_data_loader("data.json")

from src.connectors.xlsx_connector import XlsxConnector

def test_get_data_loader_xlsx():
    """Testa se get_data_loader retorna XlsxConnector para arquivos .xlsx."""
    # Act
    loader = get_data_loader("data.xlsx")

    # Assert
    assert isinstance(loader, XlsxConnector)

from .csv_connector import CsvConnector
from .xlsx_connector import XlsxConnector


def get_data_loader(file_path: str, delimiter: str = None):
    """
    Fábrica de conectores que retorna o loader apropriado com base na extensão do arquivo.

    Args:
        file_path (str): O caminho para o arquivo de dados.
        delimiter (str, optional): O delimitador a ser usado para arquivos CSV. Defaults to None.

    Returns:
        Um conector de dados apropriado para a extensão do arquivo.

    Raises:
        ValueError: Se a extensão do arquivo não for suportada.
    """
    file_ext = file_path.lower().split('.')[-1]

    if file_ext == 'csv':
        return CsvConnector(file_path, delimiter=delimiter)
    elif file_ext in ['xlsx', 'xls']:
        return XlsxConnector(file_path)
    else:
        raise ValueError(
            f"Extensão de arquivo não suportada para: {file_path}")

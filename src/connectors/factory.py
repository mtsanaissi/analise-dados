from .csv_connector import CsvConnector


def get_data_loader(file_path: str, delimiter: str = None) -> CsvConnector:
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
    if file_path.endswith('.csv'):
        return CsvConnector(file_path, delimiter=delimiter)
    else:
        raise ValueError(
            f"Extensão de arquivo não suportada para: {file_path}")

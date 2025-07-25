import pandas as pd
from typing import Any


class CsvConnector:
    """
    Conector de dados para arquivos CSV.

    Esta classe encapsula a lógica de leitura e escrita de arquivos CSV,
    abstraindo a interação direta com a biblioteca pandas.
    """

    def __init__(self, file_path: str):
        """
        Inicializa o CsvConnector.

        Args:
            file_path (str): O caminho para o arquivo CSV.
        """
        self.file_path = file_path

    def read(self, **kwargs: Any) -> pd.DataFrame:
        """
        Lê o arquivo CSV e o retorna como um DataFrame do pandas.

        Este método utiliza pd.read_csv e permite que argumentos adicionais
        sejam passados diretamente para essa função, tornando-o flexível.

        Args:
            **kwargs: Argumentos de palavra-chave a serem passados para
                      pd.read_csv (por exemplo, sep, encoding, decimal).

        Returns:
            pd.DataFrame: O conteúdo do arquivo CSV como um DataFrame.
        """
        return pd.read_csv(self.file_path, **kwargs)

    def write(self, df: pd.DataFrame, **kwargs: Any) -> None:
        """
        Salva um DataFrame em um arquivo CSV.

        Este método utiliza df.to_csv e permite que argumentos adicionais
        sejam passados diretamente para essa função. O índice do DataFrame
        não é incluído no arquivo por padrão.

        Args:
            df (pd.DataFrame): O DataFrame a ser salvo.
            **kwargs: Argumentos de palavra-chave a serem passados para
                      df.to_csv (por exemplo, sep, encoding, decimal).
        """
        kwargs.setdefault('index', False)
        df.to_csv(self.file_path, **kwargs)

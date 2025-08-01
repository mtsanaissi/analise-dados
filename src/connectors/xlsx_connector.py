# -*- coding: utf-8 -*-

# --------------------------------------------------------------------------------
# Descrição: Conector para ler e escrever dados em arquivos Excel (.xlsx).
# Autor: Gemini
# Criado em: 29/07/2025
# Versão: 1.0
# Licença: MIT
# --------------------------------------------------------------------------------

import pandas as pd
from typing import Optional

class XlsxConnector:
    """
    Conector para interagir com arquivos Excel (.xlsx).
    """

    def __init__(self, file_path: str, sheet_name: Optional[str] = None, dtype: any = None):
        """
        Inicializa o conector.

        Args:
            file_path (str): O caminho para o arquivo Excel.
            sheet_name (str, optional): O nome da planilha a ser lida. 
                                        Se None, a primeira planilha é lida. Defaults to None.
        """
        self.file_path = file_path
        self.sheet_name = sheet_name
        self.dtype = dtype

    def read(self) -> pd.DataFrame:
        """
        Lê dados de um arquivo Excel para um DataFrame.

        Returns:
            pd.DataFrame: O DataFrame lido do arquivo.
        """
        try:
            # Modificado para ler a primeira planilha por índice (0) se sheet_name não for especificado.
            sheet_to_read = self.sheet_name if self.sheet_name is not None else 0
            return pd.read_excel(self.file_path, sheet_name=sheet_to_read, dtype=self.dtype)
        except FileNotFoundError:
            raise
        except Exception as e:
            raise IOError(f"Não foi possível ler o arquivo Excel: {self.file_path}. Erro: {e}")

    def write(self, df: pd.DataFrame, index: bool = False):
        """
        Escreve um DataFrame para um arquivo Excel.

        Args:
            df (pd.DataFrame): O DataFrame a ser escrito.
            index (bool, optional): Se o índice do DataFrame deve ser escrito. Defaults to False.
        """
        try:
            # Se sheet_name for None, o nome padrão 'Sheet1' será usado.
            df.to_excel(self.file_path, sheet_name=self.sheet_name, index=index)
        except Exception as e:
            raise IOError(f"Não foi possível escrever no arquivo Excel: {self.file_path}. Erro: {e}")

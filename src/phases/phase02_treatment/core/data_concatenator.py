import logging
import os
from typing import Dict, List

import pandas as pd

from src.connectors.factory import CsvConnector
from src.utils import find_files

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class DataConcatenator:
    """
    A class to concatenate data from multiple files in a directory into a single output file.
    """

    def __init__(self, input_folder: str, output_file: str, file_type: str):
        """
        Initializes the DataConcatenator.

        Args:
            input_folder (str): Absolute path to the folder with source files.
            output_file (str): Absolute path to the output file.
            file_type (str): The type of file to concatenate ('csv', 'json', or 'xlsx').
        """
        self.input_folder = input_folder
        self.output_file = output_file
        self.file_type = file_type
        self.validate_config()

    def validate_config(self):
        """
        Validates the provided file type.
        """
        if self.file_type not in ['csv', 'json', 'xlsx']:
            raise ValueError(f"Unsupported file type: {self.file_type}. Must be 'csv', 'json', or 'xlsx'.")

    def concatenate_files(self):
        """
        Orchestrates the file concatenation process.
        """
        logging.info("Starting concatenation process...")
        try:
            files_to_process = find_files(self.input_folder, [self.file_type])
            if not files_to_process:
                logging.warning("No files found to concatenate.")
                return

            dataframes = self._read_files(files_to_process)
            if not dataframes:
                logging.warning("No data could be read from the files.")
                return

            master_df = self._concatenate_dataframes(dataframes)
            self._write_output_file(master_df)
            logging.info("Concatenation process completed successfully.")

        except Exception as e:
            logging.error(f"An error occurred during concatenation: {e}")
            raise

    def _read_files(self, files: List[str]) -> List[pd.DataFrame]:
        """
        Reads a list of files into pandas DataFrames.

        Args:
            files (List[str]): A list of file paths to read.

        Returns:
            List[pd.DataFrame]: A list of pandas DataFrames.
        """
        dataframes = []
        for file_path in files:
            try:
                logging.info(f"Reading file: {file_path}")
                if self.file_type == 'csv':
                    connector = CsvConnector(file_path=file_path)
                    df = connector.read()
                elif self.file_type == 'xlsx':
                    df = pd.read_excel(file_path)
                elif self.file_type == 'json':
                    df = pd.read_json(file_path)

                dataframes.append(df)
            except Exception as e:
                logging.error(f"Failed to read file {file_path}: {e}")
        return dataframes

    def _concatenate_dataframes(self, dataframes: List[pd.DataFrame]) -> pd.DataFrame:
        """
        Concatenates a list of DataFrames into a single DataFrame.

        Args:
            dataframes (List[pd.DataFrame]): The list of DataFrames to concatenate.

        Returns:
            pd.DataFrame: The concatenated DataFrame.
        """
        if not dataframes:
            return pd.DataFrame()

        logging.info("Concatenating DataFrames...")
        master_df = pd.concat(dataframes, ignore_index=True, sort=False)
        return master_df

    def _write_output_file(self, df: pd.DataFrame):
        """
        Writes the master DataFrame to the specified output file.

        Args:
            df (pd.DataFrame): The DataFrame to write.
        """
        logging.info(f"Writing concatenated data to {self.output_file}...")

        output_dir = os.path.dirname(self.output_file)
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        if self.file_type == 'csv':
            connector = CsvConnector(file_path=self.output_file)
            connector.write(df)
        elif self.file_type == 'xlsx':
            df.to_excel(self.output_file, index=False)
        elif self.file_type == 'json':
            df.to_json(self.output_file, orient='records', indent=4)

        logging.info("Output file written successfully.")

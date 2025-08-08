import logging
import os
from typing import Dict, List, Any

import pandas as pd

from src.connectors.factory import CsvConnector
from src.utils import find_files

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def concatenate_data(input_folder: str, output_file: str, file_type: str) -> Dict[str, Any]:
    """
    Concatenates data from multiple files in a directory into a single output file.

    Args:
        input_folder (str): Absolute path to the folder with source files.
        output_file (str): Absolute path to the output file.
        file_type (str): The type of file to concatenate ('csv', 'json', or 'xlsx').

    Returns:
        Dict[str, Any]: A dictionary with the status of the operation.
    """
    logger = logging.getLogger(__name__)
    try:
        if file_type not in ['csv', 'json', 'xlsx']:
            raise ValueError(f"Unsupported file type: {file_type}. Must be 'csv', 'json', or 'xlsx'.")

        logger.info("Starting concatenation process...")
        files_to_process = find_files(input_folder, [file_type])
        if not files_to_process:
            logger.warning("No files found to concatenate.")
            return {
                "status": "success",
                "message": "No files found to concatenate.",
                "report_path": None
            }

        dataframes = _read_files(files_to_process, file_type)
        if not dataframes:
            logger.warning("No data could be read from the files.")
            return {
                "status": "success",
                "message": "No data could be read from the files.",
                "report_path": None
            }

        master_df = _concatenate_dataframes(dataframes)
        _write_output_file(master_df, output_file, file_type)
        logger.info("Concatenation process completed successfully.")
        return {
            "status": "success",
            "message": f"Concatenation completed successfully. {len(master_df)} rows in the output file.",
            "report_path": output_file
        }
    except Exception as e:
        logger.error(f"An error occurred during concatenation: {e}")
        return {
            "status": "error",
            "message": str(e),
            "report_path": None
        }

def _read_files(files: List[str], file_type: str) -> List[pd.DataFrame]:
    dataframes = []
    logger = logging.getLogger(__name__)
    for file_path in files:
        try:
            logger.info(f"Reading file: {file_path}")
            if file_type == 'csv':
                connector = CsvConnector(file_path=file_path)
                df = connector.read()
            elif file_type == 'xlsx':
                df = pd.read_excel(file_path)
            elif file_type == 'json':
                df = pd.read_json(file_path)
            dataframes.append(df)
        except Exception as e:
            logger.error(f"Failed to read file {file_path}: {e}")
    return dataframes

def _concatenate_dataframes(dataframes: List[pd.DataFrame]) -> pd.DataFrame:
    if not dataframes:
        return pd.DataFrame()
    logger = logging.getLogger(__name__)
    logger.info("Concatenating DataFrames...")
    return pd.concat(dataframes, ignore_index=True, sort=False)

def _write_output_file(df: pd.DataFrame, output_file: str, file_type: str):
    logger = logging.getLogger(__name__)
    logger.info(f"Writing concatenated data to {output_file}...")
    output_dir = os.path.dirname(output_file)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    if file_type == 'csv':
        connector = CsvConnector(file_path=output_file)
        connector.write(df)
    elif file_type == 'xlsx':
        df.to_excel(output_file, index=False)
    elif file_type == 'json':
        df.to_json(output_file, orient='records', indent=4)
    logger.info("Output file written successfully.")

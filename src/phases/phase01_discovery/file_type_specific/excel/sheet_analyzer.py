import pandas as pd

def get_excel_columns(file_path):
    """
    Lê um arquivo Excel e retorna as colunas da primeira planilha.
    """
    try:
        # Lê apenas o cabeçalho da primeira planilha para eficiência
        df = pd.read_excel(file_path, nrows=0)
        return list(df.columns)
    except Exception:
        return []


def analyze_excel_sheets(file_path):
    """
    Analyzes the structure of sheets in an Excel (XLSX) file.

    Args:
        file_path (str): The path to the Excel file.

    Returns:
        dict: A dictionary containing the analysis status, a list of sheet information,
              and the total number of sheets.
    """
    try:
        xls = pd.ExcelFile(file_path)
        sheet_names = xls.sheet_names
        num_sheets = len(sheet_names)
        sheets_info = []

        for sheet_name in sheet_names:
            try:
                # Read a small sample of the sheet
                df_sample = pd.read_excel(file_path, sheet_name=sheet_name, nrows=10)
                num_columns = df_sample.shape[1]
                is_readable = True
                error_message = None
            except Exception as e:
                num_columns = 0
                is_readable = False
                error_message = str(e)

            sheets_info.append({
                "sheet_name": sheet_name,
                "is_readable": is_readable,
                "num_columns": num_columns,
                "error_message": error_message
            })

        return {
            "status": "success",
            "sheets_info": sheets_info,
            "num_sheets": num_sheets
        }
    except Exception as e:
        return {
            "status": "error",
            "error_message": str(e),
            "sheets_info": [],
            "num_sheets": 0
        }

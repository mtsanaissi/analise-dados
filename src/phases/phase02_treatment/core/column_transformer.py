import pandas as pd

COLUMN_TO_REMOVE_NAME = "total"

def transform_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Processa um DataFrame para remover a coluna "Total", se existir como última coluna.
    """
    if df.empty or not df.columns.any():
        return df

    last_column_name_original = df.columns[-1]
    normalized_last_column_name = str(last_column_name_original).strip().lower()

    if normalized_last_column_name == COLUMN_TO_REMOVE_NAME:
        df_modified = df.drop(columns=[last_column_name_original])
        return df_modified
    else:
        return df

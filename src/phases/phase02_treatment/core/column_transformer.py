import pandas as pd

COLUMN_TO_REMOVE_NAME = "total"
COLUMN_TO_TRANSFORM_NAME = "Dep_Time"

def transform_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Processa um DataFrame para realizar as seguintes transformações:
    1. Remove a coluna "Total", se existir como última coluna.
    2. Converte a coluna "Dep_Time" para string com formato HHMM.
    """
    df_processed = df.copy()

    if df_processed.empty or not df_processed.columns.any():
        return df_processed

    # Lógica para remover a coluna 'Total'
    last_column_name_original = df_processed.columns[-1]
    normalized_last_column_name = str(last_column_name_original).strip().lower()
    if normalized_last_column_name == COLUMN_TO_REMOVE_NAME:
        df_processed = df_processed.drop(columns=[last_column_name_original])

    # Lógica para transformar a coluna 'Dep_Time'
    if COLUMN_TO_TRANSFORM_NAME in df_processed.columns:
        # Garante que a coluna seja tratada como numérica antes de formatar
        df_processed[COLUMN_TO_TRANSFORM_NAME] = pd.to_numeric(
            df_processed[COLUMN_TO_TRANSFORM_NAME], errors='coerce'
        ).fillna(0).astype(int).astype(str).str.zfill(4)

    return df_processed

import pandas as pd

def apply_corrections(df: pd.DataFrame, corrections_map: dict) -> pd.DataFrame:
    """
    Aplica correções a um DataFrame com base em um mapa de correções.
    """
    for column_name in df.columns:
        # O método .replace() do pandas é otimizado para esse tipo de operação
        df[column_name] = df[column_name].replace(corrections_map)
    return df

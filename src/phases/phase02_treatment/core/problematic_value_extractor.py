import pandas as pd
from src.utils import has_problematic_char


def extract_values(df: pd.DataFrame, column_name_cidade="Cidade", column_name_uf="UF") -> dict | None:
    """
    Processa um DataFrame para encontrar valores com caracteres problemáticos.
    """
    problematic_entries_for_file = {}
    file_had_problems = False

    column_name_cidade_lower = column_name_cidade.lower()
    column_name_uf_lower = column_name_uf.lower()

    # Iterar sobre as células
    for col_name_original_case in df.columns:
        col_name_lower = col_name_original_case.lower()

        for row_idx, value in df[col_name_original_case].items():
            if has_problematic_char(value):
                file_had_problems = True
                display_value = str(value)

                if col_name_lower == column_name_cidade_lower:
                    uf_value = ""
                    found_uf_col_original_case = None
                    for orig_h_name in df.columns:
                        if orig_h_name.lower() == column_name_uf_lower:
                            found_uf_col_original_case = orig_h_name
                            break

                    if found_uf_col_original_case and found_uf_col_original_case in df.columns:
                        uf_value = str(
                            df.get(found_uf_col_original_case, {}).get(row_idx, "")).strip()

                    if uf_value:
                        display_value = f"{str(value).strip()} - {uf_value}"
                    else:
                        display_value = str(value).strip()

                if col_name_original_case not in problematic_entries_for_file:
                    problematic_entries_for_file[col_name_original_case] = []

                if display_value not in problematic_entries_for_file[col_name_original_case]:
                    problematic_entries_for_file[col_name_original_case].append(
                        display_value)

    if file_had_problems:
        return problematic_entries_for_file
    else:
        return None

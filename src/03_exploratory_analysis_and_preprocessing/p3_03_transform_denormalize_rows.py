# -*- coding: utf-8 -*-

# --------------------------------------------------------------------------------
# Descrição: [Manter a descrição original, se houver. Se não, adicione uma descrição concisa do propósito do script em português.]
# Exemplo de uso: python p3_03_transform_denormalize_rows.py --argumento valor
#
# Autor: Marcelo Anaissi
# Criado em: 29/05/2025
# Versão: 1.0
#
# Modificado por: Jules
# Modificado em: 21/07/2025
# Licença: MIT
# --------------------------------------------------------------------------------
import pandas as pd

df = pd.read_excel('..\data\Categorias Recomendações.xlsx')
# print(df.head())


# for each row, if Categorias column has line breaks, append new row with same Id for each string between line breaks
for i in range(len(df)):
    if df['Categorias'][i].find('\n') != -1:
        for j in range(len(df['Categorias'][i].split('\n'))):
            df.loc[len(df)] = [df['Id Recomendação'][i],
                               df['Categorias'][i].split('\n')[j]]

# remove rows that contains \n in the Categorias column
df = df[df['Categorias'].str.contains('\n') == False]

# replace content of excel file with new dataframe

df.to_excel('..\data\Categorias Recomendaçães.xlsx', index=False)

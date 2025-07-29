# -*- coding: utf-8 -*-

# --------------------------------------------------------------------------------
# Descrição: Desnormaliza um arquivo Excel onde uma coluna contém múltiplos valores
#            separados por quebras de linha, criando uma nova linha para cada valor.
# Exemplo de uso: python p3_03_transform_denormalize_rows.py --input-file input.xlsx --output-file output.xlsx
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
import argparse
import sys
import os

def denormalize_rows(input_file, output_file):
    """
    Lê um arquivo Excel, desnormaliza as linhas com base na coluna 'Categorias'
    e salva o resultado em um novo arquivo Excel.
    """
    try:
        df = pd.read_excel(input_file)
    except FileNotFoundError:
        print(f"Erro: O arquivo de entrada '{input_file}' não foi encontrado.", file=sys.stderr)
        sys.exit(1)

    # DataFrame para armazenar as novas linhas desnormalizadas
    new_rows = []

    for _, row in df.iterrows():
        categorias = str(row['Categorias'])
        id_recomendacao = row['Id Recomendação']

        # Se a célula 'Categorias' contiver quebras de linha, divida-a
        if '\n' in categorias:
            split_categorias = categorias.split('\n')
            for categoria in split_categorias:
                if categoria.strip():  # Adicionar apenas se não for uma string vazia
                    new_rows.append({'Id Recomendação': id_recomendacao, 'Categorias': categoria.strip()})
        else:
            # Se não houver quebra de linha, mantenha a linha como está
            new_rows.append({'Id Recomendação': id_recomendacao, 'Categorias': categorias.strip()})

    # Criar um novo DataFrame a partir da lista de novas linhas
    df_denormalized = pd.DataFrame(new_rows)

    # Salvar o novo DataFrame no arquivo de saída
    try:
        output_dir = os.path.dirname(output_file)
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
        df_denormalized.to_excel(output_file, index=False)
        print(f"Arquivo desnormalizado salvo com sucesso em: {output_file}")
    except Exception as e:
        print(f"Erro ao salvar o arquivo de saída '{output_file}': {e}", file=sys.stderr)
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description="Desnormaliza linhas de um arquivo Excel com base em quebras de linha na coluna 'Categorias'.",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument(
        "--input-file", type=str, required=True,
        help="Caminho para o arquivo Excel de entrada."
    )
    parser.add_argument(
        "--output-file", type=str, required=True,
        help="Caminho para o arquivo Excel de saída."
    )

    args = parser.parse_args()
    denormalize_rows(args.input_file, args.output_file)


if __name__ == "__main__":
    main()

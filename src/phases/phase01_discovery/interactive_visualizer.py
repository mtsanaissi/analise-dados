# -*- coding: utf-8 -*-

def display_interactive_report(results):
    """
    Exibe os resultados da Fase 1 de forma interativa em um ambiente Jupyter.
    """
    # Importações locais para evitar sobrecarga quando não estiver no modo interativo
    import pandas as pd
    import matplotlib.pyplot as plt
    import seaborn as sns
    from IPython.display import display, HTML, JSON
    import json

    # Extrai o dicionário de resultados detalhados
    detailed_results = results.get('detailed_results', {})

    # --- 1. Análise de Volume de Dados ---
    data_volume = detailed_results.get('data_volume_analysis', {})
    if data_volume and data_volume.get('total_files') is not None:
        display(HTML('<h2>Análise de Volume de Dados</h2>'))
        # Tabela com métricas principais
        volume_summary = {
            "Métrica": ["Total de Arquivos", "Tamanho Total (MB)"],
            "Valor": [data_volume.get('total_files', 'N/A'), f"{data_volume.get('total_size_mb', 0):.2f}"]
        }
        df_volume = pd.DataFrame(volume_summary)
        display(df_volume.to_html(index=False))

        # Gráfico de barras para os 5 maiores arquivos
        file_sizes = data_volume.get('file_sizes', [])
        if file_sizes:
            df_sizes = pd.DataFrame(file_sizes)
            df_sizes_sorted = df_sizes.sort_values(by='size_mb', ascending=False).head(5)

            plt.figure(figsize=(10, 5))
            sns.barplot(x='size_mb', y='file', data=df_sizes_sorted, palette='viridis')
            plt.title('Top 5 Maiores Arquivos')
            plt.xlabel('Tamanho (MB)')
            plt.ylabel('Arquivo')
            plt.tight_layout()
            plt.show()

    # --- 2. Análise de Encoding ---
    encoding_results = detailed_results.get('encoding_analysis', [])
    if encoding_results:
        display(HTML('<h2>Análise de Encoding</h2>'))
        # Renomeia 'file' para 'Arquivo' para consistência
        df_encoding = pd.DataFrame(encoding_results)
        df_encoding.rename(columns={'file': 'Arquivo', 'encoding': 'Encoding', 'confidence': 'Confiança'}, inplace=True)
        # Seleciona e reordena colunas para exibição
        display_cols = ['Arquivo', 'Encoding', 'Confiança', 'status', 'message']
        df_encoding_display = df_encoding[[col for col in display_cols if col in df_encoding.columns]]
        display(HTML(df_encoding_display.to_html(index=False)))

    # --- 3. Análise de Delimitador CSV ---
    delimiter_results = detailed_results.get('csv_delimiter_analysis', [])
    if delimiter_results:
        display(HTML('<h2>Análise de Delimitador CSV</h2>'))
        # Processa os resultados para criar um DataFrame limpo
        processed_delimiters = []
        for item in delimiter_results:
            file_name = item.get('file', 'N/A')
            result = item.get('result', {})
            processed_delimiters.append({
                'Arquivo': file_name,
                'Delimitador': result.get('delimiter', 'N/A'),
                'Status': result.get('status', 'N/A')
            })
        df_delimiter = pd.DataFrame(processed_delimiters)
        display(HTML(df_delimiter.to_html(index=False)))

    # --- 4. Análise de Consistência de Colunas CSV ---
    column_consistency = detailed_results.get('csv_column_consistency_analysis', {})
    if column_consistency and column_consistency.get('status') != 'error':
        display(HTML('<h2>Análise de Consistência de Colunas CSV</h2>'))
        display(HTML(f"<h4>{column_consistency.get('message', '')}</h4>"))
        if not column_consistency.get('is_consistent', True):
            structures = column_consistency.get('structures', {})
            if structures:
                # Transforma o dicionário de estruturas em um DataFrame para melhor visualização
                comparison_data = []
                for struct_key, files in structures.items():
                    # struct_key é uma tupla de nomes de colunas
                    col_str = ", ".join(struct_key)
                    for file_name in files:
                        comparison_data.append({'Estrutura de Colunas': col_str, 'Arquivo': file_name})
                df_comparison = pd.DataFrame(comparison_data)
                display(HTML("<h5>Comparação das Estruturas Encontradas:</h5>"))
                display(HTML(df_comparison.to_html(index=False)))

    # --- 5. Outras Análises (JSON, Excel, etc.) ---
    other_analyses = {
        "Análise de Integridade de Dados": detailed_results.get('data_integrity_analysis', {}),
        "Validação de Esquema JSON": detailed_results.get('json_schema_validation', []),
        "Análise de Planilhas Excel": detailed_results.get('excel_sheet_analysis', [])
    }

    # Verifica se há algum resultado em "Outras Análises" antes de exibir o título principal
    if any(other_analyses.values()):
        display(HTML('<h2>Outras Análises (Resultados em JSON)</h2>'))

    for title, analysis_result in other_analyses.items():
        if analysis_result:
            display(HTML(f"<h3>{title}</h3>"))
            # Usando IPython.display.JSON para uma visualização aninhada e interativa
            display(JSON(analysis_result))

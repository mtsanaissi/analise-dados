# -*- coding: utf-8 -*-

def display_interactive_report(results):
    """
    Exibe os resultados da Fase 1 de forma interativa em um ambiente Jupyter,
    focando em tabelas e gráficos e omitindo seções irrelevantes.
    """
    import pandas as pd
    import matplotlib.pyplot as plt
    import seaborn as sns
    from IPython.display import display, HTML

    pd.set_option('display.max_colwidth', None)
    detailed_results = results.get('detailed_results', {})

    # --- 1. Análise de Volume de Dados ---
    data_volume = detailed_results.get('data_volume_analysis', {})
    if data_volume and data_volume.get('total_files') is not None:
        display(HTML('<h2>Análise de Volume de Dados</h2>'))
        volume_summary = {
            "Métrica": ["Total de Arquivos", "Tamanho Total (MB)"],
            "Valor": [data_volume.get('total_files', 'N/A'), f"{data_volume.get('total_size_mb', 0):.2f}"]
        }
        df_volume = pd.DataFrame(volume_summary)
        display(HTML(df_volume.to_html(index=False)))

        file_sizes = data_volume.get('file_sizes', [])
        if file_sizes:
            df_sizes = pd.DataFrame(file_sizes)
            df_sizes_sorted = df_sizes.sort_values(by='size_mb', ascending=False).head(10)
            plt.figure(figsize=(12, 6))
            sns.barplot(x='size_mb', y='file', data=df_sizes_sorted, palette='viridis')
            plt.title('Top 10 Maiores Arquivos')
            plt.xlabel('Tamanho (MB)')
            plt.ylabel('Arquivo')
            plt.tight_layout()
            plt.show()

    # --- 2. Análise de Integridade e Estrutura ---
    integrity_analysis = detailed_results.get('data_integrity_analysis', {})
    integrity_reports = integrity_analysis.get('reports', [])
    if integrity_reports:
        display(HTML('<h2>Análise de Integridade e Estrutura</h2>'))
        processed_reports = []
        for report in integrity_reports:
            details = report.get('details', {})
            file_name = report.get('file_path', 'N/A').split('\\')[-1]
            
            num_columns = 'N/A'
            if 'sheets_info' in details and details.get('sheets_info'):
                num_columns = details['sheets_info'][0].get('num_columns', 'N/A')

            processed_reports.append({
                'Arquivo': file_name,
                'Tipo': report.get('file_type', 'N/A'),
                'Nº de Colunas': num_columns,
                'Status Geral': report.get('status', 'N/A'),
                'Vazio?': details.get('is_empty', False),
                'Caracteres Problemáticos?': details.get('problematic_chars_found', False)
            })
        df_integrity = pd.DataFrame(processed_reports)
        display(HTML(df_integrity.to_html(index=False)))

    # --- 3. Análise de Encoding ---
    encoding_results = detailed_results.get('encoding_analysis', [])
    analyzed_encodings = [r for r in encoding_results if r.get('status') != 'skipped']
    if analyzed_encodings:
        display(HTML('<h2>Análise de Encoding</h2>'))
        df_encoding = pd.DataFrame(analyzed_encodings)
        df_encoding['file'] = df_encoding['file'].apply(lambda x: x.split('\\')[-1])
        df_encoding.rename(columns={'file': 'Arquivo', 'encoding': 'Encoding', 'confidence': 'Confiança', 'message': 'Observação'}, inplace=True)
        display_cols = ['Arquivo', 'Encoding', 'Confiança', 'Observação']
        df_encoding_display = df_encoding[[col for col in display_cols if col in df_encoding.columns]]
        display(HTML(df_encoding_display.to_html(index=False)))

    # --- 4. Análise Específica de CSV ---
    delimiter_results = detailed_results.get('csv_delimiter_analysis', [])
    if delimiter_results:
        display(HTML('<h2>Análise de Arquivos CSV</h2>'))
        processed_delimiters = []
        for item in delimiter_results:
            result = item.get('result', {})
            processed_delimiters.append({
                'Arquivo': item.get('file', 'N/A'),
                'Delimitador Detectado': result.get('delimiter', 'N/A'),
                'Status': result.get('status', 'N/A')
            })
        df_delimiter = pd.DataFrame(processed_delimiters)
        display(HTML(df_delimiter.to_html(index=False)))

    column_consistency = detailed_results.get('csv_column_consistency_analysis', {})
    if column_consistency and not column_consistency.get('is_consistent', True):
        display(HTML('<h3>Consistência de Colunas (CSV)</h3>'))
        display(HTML(f"<b>Mensagem:</b> {column_consistency.get('message', '')}"))
        structures = column_consistency.get('structures', {})
        if structures:
            comparison_data = []
            for i, (struct_key, files) in enumerate(structures.items()):
                col_str = ", ".join(struct_key)
                for file_name in files:
                    comparison_data.append({'Grupo': f'Estrutura {i+1}', 'Arquivo': file_name.split('\\')[-1], 'Colunas': col_str})
            df_comparison = pd.DataFrame(comparison_data)
            display(HTML("<b>Comparação das Estruturas Encontradas:</b>"))
            display(HTML(df_comparison.to_html(index=False)))

    # --- 5. Análise Específica de Excel ---
    excel_analysis = detailed_results.get('excel_sheet_analysis', [])
    if excel_analysis:
        display(HTML('<h2>Análise de Arquivos Excel</h2>'))
        processed_sheets = []
        for item in excel_analysis:
            # O 'item' aqui é um dicionário com chaves 'file' e 'result'
            # O 'result' contém 'sheets_info', 'status', etc.
            result_data = item.get('result', {})
            sheets_info = result_data.get('sheets_info', [])
            sheet_names = ", ".join([s.get('sheet_name', 'N/A') for s in sheets_info])
            processed_sheets.append({
                'Arquivo': item.get('file', 'N/A').split('\\')[-1],
                'Status': result_data.get('status', 'N/A'),
                'Nº de Planilhas': len(sheets_info),
                'Nomes das Planilhas': sheet_names if sheet_names else 'N/A'
            })
        df_excel = pd.DataFrame(processed_sheets)
        display(HTML(df_excel.to_html(index=False)))

    # --- 6. Análise Específica de JSON ---
    json_validation = detailed_results.get('json_schema_validation', [])
    if json_validation:
        display(HTML('<h2>Análise de Arquivos JSON</h2>'))
        processed_json = []
        for item in json_validation:
            result = item.get('result', {})
            processed_json.append({
                'Arquivo': item.get('file', 'N/A'),
                'Status': result.get('status', 'N/A'),
                'Mensagem': result.get('message', 'N/A')
            })
        df_json = pd.DataFrame(processed_json)
        display(HTML(df_json.to_html(index=False)))
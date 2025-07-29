import pandas as pd

def generate_html_report(report_data, output_path):
    """
    Generates an HTML report from the discovery phase data.

    Args:
        report_data (dict): The results wrapper dictionary.
        output_path (str): The path to save the HTML report.
    """
    html_content = """
    <html>
    <head>
        <title>Relatório de Descoberta de Dados</title>
        <style>
            body { font-family: sans-serif; }
            h1, h2 { color: #333; }
            table { border-collapse: collapse; width: 100%; }
            th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
            th { background-color: #f2f2f2; }
        </style>
    </head>
    <body>
        <h1>Relatório de Descoberta de Dados</h1>
    """

    for section, data in report_data.items():
        html_content += f"<h2>{section.replace('_', ' ').title()}</h2>"
        if isinstance(data, dict):
            if not data:
                html_content += "<p>Nenhum dado disponível.</p>"
            # Check if the dictionary values are also dictionaries (nested dict)
            elif isinstance(list(data.values())[0], dict):
                df = pd.DataFrame.from_dict(data, orient='index')
                html_content += df.to_html()
            else:
                # Simple key-value dictionary
                df = pd.DataFrame.from_dict(data, orient='index', columns=['Value'])
                html_content += df.to_html()
        elif isinstance(data, list):
             # Convert list of dicts to DataFrame
            df = pd.DataFrame(data)
            html_content += df.to_html(index=False)
        else:
            html_content += f"<p>{data}</p>"

    html_content += """
    </body>
    </html>
    """

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_content)

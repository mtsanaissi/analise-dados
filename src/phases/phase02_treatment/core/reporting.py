# -*- coding: utf-8 -*-

import json
import logging


def generate_json_report(report_data, output_path):
    """
    Gera um relatório JSON formatado a partir de um dicionário de dados.

    Args:
        report_data (dict): Dicionário contendo os dados do relatório.
        output_path (str): Caminho onde o arquivo JSON será salvo.
    """
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=4, ensure_ascii=False)
        logging.info(f"Relatório JSON gerado com sucesso em: {output_path}")
    except IOError as e:
        logging.error(f"Erro ao escrever o relatório JSON em {output_path}: {e}")
    except TypeError as e:
        logging.error(f"Erro de tipo ao gerar o relatório JSON: {e}")


def generate_html_report(report_data, output_path):
    """
    Gera um relatório HTML a partir de um dicionário de dados.

    Args:
        report_data (dict): Dicionário contendo os dados do relatório.
        output_path (str): Caminho onde o arquivo HTML será salvo.
    """
    summary = report_data.get("summary", {})
    details = report_data.get("details", [])

    html_content = f"""
    <!DOCTYPE html>
    <html lang="pt-br">
    <head>
        <meta charset="UTF-8">
        <title>Relatório de Tratamento da Fase 2</title>
        <style>
            body {{ font-family: sans-serif; margin: 2em; }}
            h1, h2 {{ color: #333; }}
            table {{ border-collapse: collapse; width: 100%; margin-bottom: 2em; }}
            th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
            th {{ background-color: #f2f2f2; }}
            .summary-table td {{ font-weight: bold; }}
            .details-section {{ margin-top: 2em; }}
        </style>
    </head>
    <body>
        <h1>Relatório de Tratamento da Fase 2</h1>

        <h2>Resumo</h2>
        <table class="summary-table">
            <tr>
                <td>Total de Arquivos Processados</td>
                <td>{summary.get('total_files', 0)}</td>
            </tr>
            <tr>
                <td>Processados com Sucesso</td>
                <td>{summary.get('processed_successfully', 0)}</td>
            </tr>
            <tr>
                <td>Falhas</td>
                <td>{summary.get('failed', 0)}</td>
            </tr>
        </table>

        <div class="details-section">
            <h2>Detalhes por Arquivo</h2>
            {''.join([_generate_html_for_file(item) for item in details])}
        </div>
    </body>
    </html>
    """

    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        logging.info(f"Relatório HTML gerado com sucesso em: {output_path}")
    except IOError as e:
        logging.error(f"Erro ao escrever o relatório HTML em {output_path}: {e}")


def _generate_html_for_file(detail_item):
    """
    Gera um bloco HTML para um único item de detalhe.
    """
    file_name = detail_item.get('file_name', 'N/A')
    status = detail_item.get('status', 'N/A')
    applied_corrections = detail_item.get('applied_corrections', {})
    problematic_values = detail_item.get('problematic_values', {})

    # Correções
    corrections_rows = "".join(
        f"<tr><td>{key}</td><td>{value}</td></tr>"
        for key, value in applied_corrections.items()
    ) if applied_corrections else "<tr><td colspan='2'>Nenhuma correção aplicada.</td></tr>"

    # Valores problemáticos
    problems_rows = "".join(
        f"<tr><td>{col}</td><td>{', '.join(map(str, vals))}</td></tr>"
        for col, vals in problematic_values.items()
    ) if problematic_values else "<tr><td colspan='2'>Nenhum valor problemático encontrado.</td></tr>"

    return f"""
    <section>
        <h3>Arquivo: {file_name}</h3>
        <p><strong>Status:</strong> {status}</p>

        <h4>Correções Aplicadas</h4>
        <table>
            <thead><tr><th>De</th><th>Para</th></tr></thead>
            <tbody>{corrections_rows}</tbody>
        </table>

        <h4>Valores Problemáticos Encontrados</h4>
        <table>
            <thead><tr><th>Coluna</th><th>Valores</th></tr></thead>
            <tbody>{problems_rows}</tbody>
        </table>
    </section>
    <hr>
    """

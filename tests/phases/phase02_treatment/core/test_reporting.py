# -*- coding: utf-8 -*-

import json
import os
from src.phases.phase02_treatment.core.reporting import generate_json_report, generate_html_report

# Dados de amostra para os testes
SAMPLE_REPORT_DATA = {
    "summary": {
        "total_files": 2,
        "processed_successfully": 1,
        "failed": 1,
    },
    "details": [
        {
            "file_name": "test1.csv",
            "status": "Success",
            "applied_corrections": {"old": "new"},
            "problematic_values": {"col1": ["old"]},
        },
        {
            "file_name": "test2.csv",
            "status": "Failed",
            "applied_corrections": {},
            "problematic_values": {},
        },
    ],
}


def test_generate_json_report(tmp_path):
    """
    Testa a geração de um relatório JSON.
    Verifica se o arquivo é criado e se o conteúdo corresponde ao esperado.
    """
    # Definir o caminho do arquivo de saída
    output_path = tmp_path / "report.json"

    # Gerar o relatório
    generate_json_report(SAMPLE_REPORT_DATA, str(output_path))

    # Verificar se o arquivo foi criado
    assert os.path.exists(output_path)

    # Ler e verificar o conteúdo
    with open(output_path, "r", encoding="utf-8") as f:
        loaded_data = json.load(f)

    assert loaded_data == SAMPLE_REPORT_DATA


def test_generate_html_report(tmp_path):
    """
    Testa a geração de um relatório HTML.
    Verifica se o arquivo é criado e contém strings-chave esperadas.
    """
    # Definir o caminho do arquivo de saída
    output_path = tmp_path / "report.html"

    # Gerar o relatório
    generate_html_report(SAMPLE_REPORT_DATA, str(output_path))

    # Verificar se o arquivo foi criado
    assert os.path.exists(output_path)

    # Ler o conteúdo e verificar a presença de elementos-chave
    with open(output_path, "r", encoding="utf-8") as f:
        html_content = f.read()

    # Verificar título e cabeçalhos
    assert "<h1>Relatório de Tratamento da Fase 2</h1>" in html_content
    assert "<h2>Resumo</h2>" in html_content
    assert "<h2>Detalhes por Arquivo</h2>" in html_content

    # Verificar dados do resumo
    assert "<td>Total de Arquivos Processados</td>" in html_content
    assert f"<td>{SAMPLE_REPORT_DATA['summary']['total_files']}</td>" in html_content

    # Verificar detalhes dos arquivos
    assert "<h3>Arquivo: test1.csv</h3>" in html_content
    assert "<p><strong>Status:</strong> Success</p>" in html_content
    assert "<td>test2.csv</td>" not in html_content  # Simplificando a verificação
    assert "<h3>Arquivo: test2.csv</h3>" in html_content
    assert "<p><strong>Status:</strong> Failed</p>" in html_content

import os
from src.phases.phase01_discovery.core.reporting import generate_html_report

def test_generate_html_report(tmp_path):
    """
    Tests the generation of the HTML report.
    """
    report_data = {
        "encoding_analysis": [
            {"file": "test.csv", "encoding": "utf-8"}
        ],
        "data_volume_analysis": {
            "total_files": 1,
            "total_size_mb": 0.01
        }
    }
    output_path = os.path.join(tmp_path, "report.html")

    generate_html_report(report_data, output_path)

    assert os.path.exists(output_path)

    with open(output_path, 'r', encoding='utf-8') as f:
        html_content = f.read()
    assert "<h1>Relatório de Descoberta de Dados</h1>" in html_content
    assert "<h2>Encoding Analysis</h2>" in html_content
    assert "<h2>Data Volume Analysis</h2>" in html_content
    assert "<td>test.csv</td>" in html_content
    assert "<td>utf-8</td>" in html_content
    assert "<th>total_files</th>" in html_content
    assert "<td>1.00</td>" in html_content

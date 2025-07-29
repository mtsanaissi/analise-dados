import os
import pandas as pd
from src.phases.phase04_visualization.tool_generate_html_profiles import generate_profiles

def test_generate_profiles(tmp_path):
    # Criar diretórios de entrada e saída temporários
    input_dir = tmp_path / "input"
    output_dir = tmp_path / "output"
    input_dir.mkdir()
    output_dir.mkdir()

    # Criar um arquivo CSV de exemplo
    data = {'col1': [1, 2], 'col2': [3, 4]}
    df = pd.DataFrame(data)
    csv_path = input_dir / "test_data.csv"
    df.to_csv(csv_path, index=False)

    # Chamar a função para gerar o perfil
    generate_profiles(
        root_dir=str(input_dir),
        output_dir=str(output_dir),
        extensions=['csv'],
        recursive=False,
        delimiter=','
    )

    # Verificar se o arquivo HTML foi criado
    expected_html_path = output_dir / "test_data_profile.html"
    assert expected_html_path.exists()

    # Verificar se o nome do arquivo de entrada está no conteúdo do HTML
    html_content = expected_html_path.read_text(encoding="utf-8")
    assert "test_data.csv" in html_content

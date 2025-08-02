# -*- coding: utf-8 -*-

import os
import shutil
import pytest
from src.utils import find_files

@pytest.fixture
def temp_dir_structure():
    """Cria uma estrutura de diretórios temporária para os testes."""
    test_root = "temp_test_find_files"

    # Estrutura de diretórios e arquivos
    structure = {
        "data": ["file1.txt", "sub_data/file2.csv"],
        "fad-metadados": ["meta.json"],
        "fad-config": ["config.yml"],
        "fad-bkp-old-123": ["backup1.dat"],
        "fad-bkp-current-456": ["backup2.dat"],
        "another_excluded_dir": ["another_file.log"]
    }

    # Remove diretório de teste anterior, se existir
    if os.path.exists(test_root):
        shutil.rmtree(test_root)

    # Cria os diretórios e arquivos
    for base, contents in structure.items():
        dir_path = os.path.join(test_root, base)
        for item in contents:
            item_path = os.path.join(dir_path, item)
            os.makedirs(os.path.dirname(item_path), exist_ok=True)
            with open(item_path, "w") as f:
                f.write("test")

    yield test_root

    # Teardown - remove a estrutura de diretórios após o teste
    shutil.rmtree(test_root)

def test_find_files_exclusion_logic(temp_dir_structure):
    """
    Testa se a função find_files exclui corretamente os diretórios padrão
    e os diretórios adicionais passados como argumento.
    """
    test_root = temp_dir_structure

    # Chama a função find_files, excluindo um diretório de backup específico
    # e esperando que os padrões ('fad-metadados', 'fad-config', 'fad-bkp*') também sejam excluídos.
    found_files = find_files(
        root_path=test_root,
        extensions=["txt", "csv", "json", "yml", "dat", "log"],
        recursive=True,
        exclude_dirs=["fad-bkp-current-456", "another_excluded_dir"] # Adiciona uma exclusão específica
    )

    # Normaliza os caminhos para verificação
    found_basenames = sorted([os.path.basename(p) for p in found_files])

    # Arquivos esperados (apenas os da pasta 'data')
    expected_basenames = sorted(["file1.txt", "file2.csv"])

    # Verificações
    assert len(found_files) == 2, f"Esperava encontrar 2 arquivos, mas encontrou {len(found_files)}"
    assert found_basenames == expected_basenames, \
        f"Os arquivos encontrados ({found_basenames}) não correspondem aos esperados ({expected_basenames})."

    # Verificação explícita de que nenhum arquivo de NENHUM diretório excluído foi retornado
    all_files_in_tree = []
    for root, _, files in os.walk(test_root):
        for name in files:
            all_files_in_tree.append(os.path.join(root, name))

    excluded_files = [
        "meta.json",
        "config.yml",
        "backup1.dat",
        "backup2.dat"
    ]

    for f_path in found_files:
        basename = os.path.basename(f_path)
        assert basename not in excluded_files, f"O arquivo excluído '{basename}' foi encontrado indevidamente."

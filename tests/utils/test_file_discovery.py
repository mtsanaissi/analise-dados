# -*- coding: utf-8 -*-
import os
import pytest
from src import utils

def test_find_files_combines_default_and_custom_exclusions(tmp_path):
    """
    Valida se a função find_files combina corretamente a lista de exclusão
    padrão com uma lista personalizada fornecida via argumento, garantindo
    que nenhum dos diretórios (padrão ou customizado) seja incluído na busca.
    """
    # 1. Criar uma estrutura de diretórios de teste
    # Diretórios que devem ser ignorados por padrão
    (tmp_path / "fad-metadados").mkdir()
    (tmp_path / "fad-metadados" / "meta.csv").write_text("metadata")

    (tmp_path / "fad-config").mkdir()
    (tmp_path / "fad-config" / "config.csv").write_text("config data")

    (tmp_path / "fad-bkp-old-123").mkdir()
    (tmp_path / "fad-bkp-old-123" / "old_backup.csv").write_text("old backup")

    # Diretório que será passado como exclusão customizada
    current_backup_dir = tmp_path / "fad-bkp-current-456"
    current_backup_dir.mkdir()
    (current_backup_dir / "current_backup.csv").write_text("current backup")

    # Diretório com dados válidos que devem ser encontrados
    valid_data_dir = tmp_path / "valid_data"
    valid_data_dir.mkdir()
    valid_file = valid_data_dir / "data.csv"
    valid_file.write_text("this is valid data")

    # 2. Chamar find_files passando o diretório de backup atual para ser excluído
    found_files = utils.find_files(
        str(tmp_path),
        ["csv"],
        exclude_dirs=[os.path.basename(str(current_backup_dir))]
    )

    # 3. Assertar que apenas o arquivo válido foi encontrado
    assert len(found_files) == 1
    assert str(valid_file) in found_files

    # Checagem extra para garantir que nenhum dos arquivos excluídos está na lista
    abs_paths_to_check = [
        str(tmp_path / "fad-metadados" / "meta.csv"),
        str(tmp_path / "fad-config" / "config.csv"),
        str(tmp_path / "fad-bkp-old-123" / "old_backup.csv"),
        str(current_backup_dir / "current_backup.csv"),
    ]

    for excluded_path in abs_paths_to_check:
        assert excluded_path not in found_files

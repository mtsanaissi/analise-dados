#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pytest
import os
from src.utils import has_problematic_char, find_files

# Testes para has_problematic_char

def test_has_problematic_char_with_replacement_char():
    """Testa se o caractere de substituição Unicode (U+FFFD) é detectado."""
    problematic_string = "Este é um texto com problema: " + chr(0xfffd)
    assert has_problematic_char(problematic_string) is True

def test_has_problematic_char_with_control_char():
    """Testa se um caractere de controle não padrão (ex: U+0001) é detectado."""
    assert has_problematic_char("Texto com caractere de controle: \x01") is True

def test_has_problematic_char_with_normal_string():
    """Testa uma string normal sem caracteres problemáticos."""
    assert has_problematic_char("Um texto limpo e sem problemas.") is False

def test_has_problematic_char_with_allowed_chars():
    """Testa se caracteres de controle permitidos (tab, newline) não são detectados."""
    assert has_problematic_char("Texto com\tTAB e\nquebra de linha.") is False

def test_has_problematic_char_with_empty_string():
    """Testa se uma string vazia é tratada corretamente."""
    assert has_problematic_char("") is False

def test_has_problematic_char_with_non_string_input():
    """Testa se a função lida com input que não é string."""
    assert has_problematic_char(None) is False
    assert has_problematic_char(123) is False
    assert has_problematic_char(["lista"]) is False

# Testes para find_files

@pytest.fixture
def test_file_structure(tmp_path):
    """Cria uma estrutura de arquivos e diretórios para os testes."""
    (tmp_path / "file1.txt").touch()
    (tmp_path / "file2.csv").touch()
    (tmp_path / "subdir").mkdir()
    (tmp_path / "subdir" / "file3.txt").touch()
    (tmp_path / "subdir" / "file4.log").touch()
    return tmp_path

def test_find_files_recursive(test_file_structure):
    """Testa a busca recursiva de arquivos."""
    found_files = find_files(str(test_file_structure), ["txt"], recursive=True)
    assert len(found_files) == 2
    assert str(test_file_structure / "file1.txt") in found_files
    assert str(test_file_structure / "subdir" / "file3.txt") in found_files

def test_find_files_non_recursive(test_file_structure):
    """Testa a busca não recursiva de arquivos."""
    found_files = find_files(str(test_file_structure), ["txt"], recursive=False)
    assert len(found_files) == 1
    assert str(test_file_structure / "file1.txt") in found_files

def test_find_files_multiple_extensions(test_file_structure):
    """Testa a busca com múltiplas extensões."""
    found_files = find_files(str(test_file_structure), ["csv", "log"], recursive=True)
    assert len(found_files) == 2
    assert str(test_file_structure / "file2.csv") in found_files
    assert str(test_file_structure / "subdir" / "file4.log") in found_files

def test_find_files_no_matches(test_file_structure):
    """Testa o caso em que nenhuma extensão corresponde."""
    found_files = find_files(str(test_file_structure), ["zip"], recursive=True)
    assert len(found_files) == 0

def test_find_files_invalid_directory():
    """Testa o comportamento com um diretório inválido."""
    found_files = find_files("diretorio_invalido", ["txt"], recursive=True)
    assert len(found_files) == 0
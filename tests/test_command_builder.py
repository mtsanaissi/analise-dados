# -*- coding: utf-8 -*-

# --------------------------------------------------------------------------------
# Descrição: Testes de unidade para a lógica de construção de comandos da UI.
# Autor: Jules
# Criado em: 02/08/2025
# Versão: 1.0
# --------------------------------------------------------------------------------

import sys
import os
import pytest

# Adiciona o diretório 'src' ao sys.path para importação do módulo
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from utils import build_command

# --- Testes Base ---

def test_build_base_command():
    """Testa a construção do comando base sem argumentos extras."""
    command = build_command("data/sample", "discovery")
    assert "-d" in command
    assert "data/sample" in command
    assert "-p" in command
    assert "discovery" in command
    # python_executable, run.py, -d, path, -p, phase
    assert len(command) == 6

# --- Testes da Fase de Discovery ---

def test_build_discovery_command_with_compare_fields():
    """Testa a adição do argumento --compare-fields."""
    args = {"compare_fields": True}
    command = build_command("data/sample", "discovery", discovery_args=args)
    assert "--compare-fields" in command

def test_build_discovery_command_with_compare_types():
    """Testa a adição do argumento --compare-types."""
    args = {"compare_types": True}
    command = build_command("data/sample", "discovery", discovery_args=args)
    assert "--compare-types" in command

def test_build_discovery_command_with_report_output():
    """Testa a adição do argumento --report-output."""
    args = {"report_output": "html"}
    command = build_command("data/sample", "discovery", discovery_args=args)
    assert "--report-output" in command
    assert "html" in command

def test_build_discovery_command_with_char_cleanup():
    """Testa a adição do argumento --generate-char-cleanup-config."""
    args = {"char_cleanup_path": "config.yaml"}
    command = build_command("data/sample", "discovery", discovery_args=args)
    assert "--generate-char-cleanup-config" in command
    assert "config.yaml" in command

def test_build_discovery_command_with_all_args():
    """Testa a combinação de todos os argumentos da fase de Discovery."""
    args = {
        "compare_fields": True,
        "compare_types": True,
        "report_output": "html",
        "char_cleanup_path": "config.yaml"
    }
    command = build_command("data/sample", "discovery", discovery_args=args)
    assert "--compare-fields" in command
    assert "--compare-types" in command
    assert "--report-output" in command
    assert "html" in command
    assert "--generate-char-cleanup-config" in command
    assert "config.yaml" in command

# --- Testes da Fase de Treatment ---

def test_build_treatment_command_no_op():
    """Testa a construção do comando de tratamento sem uma operação selecionada."""
    args = {"operation": "Selecione uma operação"}
    command = build_command("data/sample", "treatment", treatment_args=args)
    # Nenhum argumento de operação deve ser adicionado
    assert len(command) == 6

def test_build_treatment_command_strip_whitespace():
    """Testa a operação de remover espaços."""
    args = {"operation": "Remover Espaços"}
    command = build_command("data/sample", "treatment", treatment_args=args)
    assert "--strip-whitespace" in command

def test_build_treatment_command_replace_values_with_config():
    """Testa a operação de substituir valores com um arquivo de configuração."""
    args = {
        "operation": "Substituir Valores",
        "config_file_path": "/tmp/replace.yaml"
    }
    command = build_command("data/sample", "treatment", treatment_args=args)
    assert "--replace-values" in command
    assert "/tmp/replace.yaml" in command

def test_build_treatment_command_find_and_replace_with_config():
    """Testa a operação de encontrar e substituir com um arquivo de configuração."""
    args = {
        "operation": "Encontrar e Substituir Texto",
        "config_file_path": "/tmp/find.yaml"
    }
    command = build_command("data/sample", "treatment", treatment_args=args)
    assert "--find-and-replace-text" in command
    assert "/tmp/find.yaml" in command

def test_build_treatment_command_concatenate_with_args():
    """Testa a operação de concatenar com os novos argumentos da CLI."""
    args = {
        "operation": "Concatenar Dados",
        "input_folder": "input",
        "output_file": "output.csv",
        "file_type": "csv"
    }
    command = build_command("data/sample", "treatment", treatment_args=args)
    assert "--concatenate-data" in command
    assert "--input-folder" in command
    assert "input" in command
    assert "--output-file" in command
    assert "output.csv" in command
    assert "--file-type" in command
    assert "csv" in command

def test_build_treatment_command_enrich_with_args():
    """Testa a operação de enriquecer com os novos argumentos da CLI."""
    args = {
        "operation": "Enriquecer Dados",
        "main_file": "main.csv",
        "lookup_file": "lookup.csv",
        "main_key": "id",
        "lookup_key": "id",
        "columns_to_add": ["col1", "col2"],
        "output_file": "enriched.csv"
    }
    command = build_command("data/sample", "treatment", treatment_args=args)
    assert "--enrich-data" in command
    assert "--main-file" in command
    assert "main.csv" in command
    assert "--lookup-file" in command
    assert "lookup.csv" in command
    assert "--main-key" in command
    assert "id" in command
    assert "--lookup-key" in command
    assert "id" in command
    assert "--columns-to-add" in command
    assert "col1" in command
    assert "col2" in command
    assert "--output-file" in command
    assert "enriched.csv" in command

def test_build_treatment_command_with_config_missing():
    """Testa uma operação que requer config mas o caminho não é fornecido."""
    args = {"operation": "Substituir Valores", "config_file_path": None}
    command = build_command("data/sample", "treatment", treatment_args=args)
    assert "--replace-values" in command
    # O comando não deve incluir o caminho se ele for None
    assert len(command) == 7

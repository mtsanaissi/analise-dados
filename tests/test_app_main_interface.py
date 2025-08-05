# -*- coding: utf-8 -*-

import unittest
from unittest.mock import patch, MagicMock
from src.app_main_interface import find_report_path
from src.utils import build_command

class TestAppMainInterface(unittest.TestCase):

    def test_find_report_path_success(self):
        output = "INFO: ...\nINFO: Relatório salvo em: /path/to/report.html\nINFO: ..."
        self.assertEqual(find_report_path(output), "/path/to/report.html")

    def test_find_report_path_no_path(self):
        output = "INFO: ...\nINFO: Execução concluída.\nINFO: ..."
        self.assertIsNone(find_report_path(output))

    def test_find_report_path_empty_output(self):
        output = ""
        self.assertIsNone(find_report_path(output))

    def test_find_report_path_with_trailing_spaces(self):
        output = "INFO: Relatório salvo em: /path/to/report.html   "
        self.assertEqual(find_report_path(output), "/path/to/report.html")

class TestBuildCommand(unittest.TestCase):

    def test_build_command_discovery(self):
        """
        Testa a construção de comando para a fase de Discovery.
        """
        command = build_command(
            "data/sample", "discovery",
            discovery_args={"compare_fields": True, "report_output": "html"},
            treatment_args={}
        )
        self.assertIn("--compare-fields", command)
        self.assertIn("--report-output", command)
        self.assertIn("html", command)

    def test_build_command_treatment_with_config(self):
        """
        Testa a construção de comando para a fase de Treatment com arquivo de configuração.
        """
        command = build_command(
            "data/sample", "treatment",
            discovery_args={},
            treatment_args={"operation": "Substituir Valores", "config_file_path": "/tmp/config.yaml"}
        )
        self.assertIn("--replace-values", command)
        self.assertIn("/tmp/config.yaml", command)

    def test_build_command_treatment_no_config(self):
        """
        Testa a construção de comando para a fase de Treatment sem arquivo de configuração.
        """
        command = build_command(
            "data/sample", "treatment",
            discovery_args={},
            treatment_args={"operation": "Remover Espaços"}
        )
        self.assertIn("--strip-whitespace", command)

if __name__ == '__main__':
    unittest.main()

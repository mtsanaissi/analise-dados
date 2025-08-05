# -*- coding: utf-8 -*-

import unittest
from unittest.mock import patch
from src.app_main_interface import find_report_path

class TestAppMainInterface(unittest.TestCase):

    def test_find_report_path_success(self):
        """
        Testa se o caminho do relatório é encontrado com sucesso.
        """
        output = "INFO: ...\nINFO: Relatório salvo em: /path/to/report.html\nINFO: ..."
        self.assertEqual(find_report_path(output), "/path/to/report.html")

    def test_find_report_path_no_path(self):
        """
        Testa o comportamento quando nenhum caminho de relatório está presente.
        """
        output = "INFO: ...\nINFO: Execução concluída.\nINFO: ..."
        self.assertIsNone(find_report_path(output))

    def test_find_report_path_empty_output(self):
        """
        Testa o comportamento com uma saída vazia.
        """
        output = ""
        self.assertIsNone(find_report_path(output))

    def test_find_report_path_with_trailing_spaces(self):
        """
        Testa se os espaços em branco no final do caminho são removidos.
        """
        output = "INFO: Relatório salvo em: /path/to/report.html   "
        self.assertEqual(find_report_path(output), "/path/to/report.html")

if __name__ == '__main__':
    unittest.main()

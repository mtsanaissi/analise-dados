# -*- coding: utf-8 -*-

import os
import json
import shutil
import unittest
import pandas as pd
from src.phases.phase01_discovery.phase01_orchestrator import run_discovery_phase
from src.utils import METADATA_DIR

class TestTypeConsistencyChecker(unittest.TestCase):

    def setUp(self):
        """Configura um ambiente de teste limpo antes de cada teste."""
        self.test_dir = "temp_test_type_consistency"
        os.makedirs(self.test_dir, exist_ok=True)

    def tearDown(self):
        """Remove o ambiente de teste após a execução de cada teste."""
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def _create_file(self, filename, content):
        """Cria um arquivo com o conteúdo especificado no diretório de teste."""
        with open(os.path.join(self.test_dir, filename), 'w', encoding='utf-8') as f:
            f.write(content)

    def test_compare_types_for_csv(self):
        """
        Testa a funcionalidade --compare-types com arquivos CSV que possuem
        inconsistências de tipos de dados.
        """
        # 1. Criar arquivos de teste de uma só vez
        self._create_file("01_reference.csv", "id,name,value,date\n1,A,10.1,2025-01-01")
        self._create_file("02_consistent.csv", "id,name,value,date\n2,B,20.2,2025-01-02")
        self._create_file("03_inconsistent.csv", "id,name,value,date\n3,C,thirty,2025-01-03") # Inconsistência clara
        self._create_file("04_different_cols.csv", "id,name,extra_col\n4,D,extra_value")
        self._create_file("unrelated.txt", "this is not a csv file")

        # 2. Executar a fase de descoberta
        extra_args = ["--compare-types", "--report-output", "json"]
        run_discovery_phase(self.test_dir, extra_args, extensions=['csv'])

        # 3. Ler o relatório gerado
        report_path = os.path.join(self.test_dir, METADATA_DIR, "discovery_report.json")
        self.assertTrue(os.path.exists(report_path), "O relatório JSON não foi gerado.")

        with open(report_path, 'r', encoding='utf-8') as f:
            report_data = json.load(f)

        # 4. Validar os resultados
        analysis_results = report_data.get("detailed_results", {}).get("type_consistency_analysis", [])
        self.assertEqual(len(analysis_results), 4, "Deveria haver 4 resultados na análise de consistência de tipo para CSV.")

        results_by_file = {res['file']: res for res in analysis_results}

        # Validações
        self.assertEqual(results_by_file["01_reference.csv"]["status"], "referencia")
        self.assertEqual(results_by_file["02_consistent.csv"]["status"], "consistente")
        self.assertEqual(results_by_file["04_different_cols.csv"]["status"], "consistente")

        inconsistent_result = results_by_file["03_inconsistent.csv"]
        self.assertEqual(inconsistent_result["status"], "inconsistente")
        self.assertEqual(len(inconsistent_result["inconsistencies"]), 1)
        inconsistency = inconsistent_result["inconsistencies"][0]
        self.assertEqual(inconsistency["column"], "value")
        self.assertEqual(inconsistency["reference_type"], "Numérico")
        self.assertEqual(inconsistency["current_type"], "Categórico/Texto")

    def _create_excel_file(self, filename, data_dict):
        """Cria um arquivo Excel com os dados fornecidos."""
        df = pd.DataFrame(data_dict)
        df.to_excel(os.path.join(self.test_dir, filename), index=False)

    def test_compare_types_for_excel_and_json(self):
        """
        Testa a funcionalidade --compare-types para arquivos Excel e JSON.
        """
        # 1. Criar arquivos de teste Excel
        self._create_excel_file("01_ref.xlsx", {"id": [1], "user": ["user_a"], "amount": [100.5]})
        self._create_excel_file("02_consistent.xlsx", {"id": [2], "user": ["user_b"], "amount": [200.0]})
        self._create_excel_file("03_inconsistent.xlsx", {"id": [3], "user": ["user_c"], "amount": ["not a number"]})

        # 2. Criar arquivos de teste JSON
        self._create_file("01_ref.json", '{"id": 1, "product": "A", "price": 9.99}\n')
        self._create_file("02_consistent.json", '{"id": 2, "product": "B", "price": 19.99}\n')
        self._create_file("03_inconsistent.json", '{"id": 3, "product": "C", "price": "free"}\n')

        # 3. Executar a fase de descoberta
        extra_args = ["--compare-types", "--report-output", "json"]
        run_discovery_phase(self.test_dir, extra_args, extensions=['xlsx', 'json'])

        # 4. Ler o relatório
        report_path = os.path.join(self.test_dir, METADATA_DIR, "discovery_report.json")
        self.assertTrue(os.path.exists(report_path))
        with open(report_path, 'r', encoding='utf-8') as f:
            report_data = json.load(f)

        analysis_results = report_data.get("detailed_results", {}).get("type_consistency_analysis", [])
        self.assertEqual(len(analysis_results), 6, "Deveria haver 6 resultados (3 Excel, 3 JSON).")

        results_by_file = {res['file']: res for res in analysis_results}

        # 5. Validar resultados do Excel
        self.assertEqual(results_by_file["01_ref.xlsx"]["status"], "referencia")
        self.assertEqual(results_by_file["02_consistent.xlsx"]["status"], "consistente")
        excel_inconsistent = results_by_file["03_inconsistent.xlsx"]
        self.assertEqual(excel_inconsistent["status"], "inconsistente")
        self.assertEqual(excel_inconsistent["inconsistencies"][0]["column"], "amount")
        self.assertEqual(excel_inconsistent["inconsistencies"][0]["reference_type"], "Numérico")
        self.assertEqual(excel_inconsistent["inconsistencies"][0]["current_type"], "Categórico/Texto")

        # 6. Validar resultados do JSON
        self.assertEqual(results_by_file["01_ref.json"]["status"], "referencia")
        self.assertEqual(results_by_file["02_consistent.json"]["status"], "consistente")
        json_inconsistent = results_by_file["03_inconsistent.json"]
        self.assertEqual(json_inconsistent["status"], "inconsistente")
        self.assertEqual(json_inconsistent["inconsistencies"][0]["column"], "price")
        self.assertEqual(json_inconsistent["inconsistencies"][0]["reference_type"], "Numérico")
        self.assertEqual(json_inconsistent["inconsistencies"][0]["current_type"], "Categórico/Texto")

if __name__ == '__main__':
    unittest.main()

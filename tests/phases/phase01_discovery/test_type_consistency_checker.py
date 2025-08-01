# -*- coding: utf-8 -*-

import os
import json
import shutil
import unittest
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

    def test_compare_types_with_inconsistencies(self):
        """
        Testa a funcionalidade --compare-types com arquivos CSV que possuem
        inconsistências de tipos de dados.
        """
        # 1. Criar arquivos de teste
        # Renomeamos os arquivos para garantir a ordem de processamento alfabética
        self._create_file("01_reference.csv", "id,name,value,date\n1,A,10.1,2025-01-01")
        self._create_file("02_consistent.csv", "id,name,value,date\n2,B,20.2,2025-01-02")
        self._create_file("03_inconsistent.csv", "id,name,value,date\n3,C,30,2025-01-03") # 'value' é numérico, mas sem casa decimal
        self._create_file("04_different_cols.csv", "id,name,extra_col\n4,D,extra_value")
        self._create_file("unrelated.txt", "this is not a csv file")

        # 2. Executar a fase de descoberta com --compare-types
        extra_args = ["--compare-types", "--report-output", "json"]
        run_discovery_phase(self.test_dir, extra_args, extensions=['csv'])

        # 3. Ler o relatório gerado
        report_path = os.path.join(self.test_dir, METADATA_DIR, "discovery_report.json")
        self.assertTrue(os.path.exists(report_path), "O relatório JSON não foi gerado.")

        with open(report_path, 'r', encoding='utf-8') as f:
            report_data = json.load(f)

        # 4. Validar os resultados
        analysis_results = report_data.get("detailed_results", {}).get("type_consistency_analysis", [])
        self.assertEqual(len(analysis_results), 4, "Deveria haver 4 resultados na análise de consistência de tipo.")

        # Mapeia os resultados por nome de arquivo para facilitar a validação
        results_by_file = {res['file']: res for res in analysis_results}

        # Valida o arquivo de referência
        self.assertIn("01_reference.csv", results_by_file)
        self.assertEqual(results_by_file["01_reference.csv"]["status"], "referencia")

        # Valida o arquivo consistente
        self.assertIn("02_consistent.csv", results_by_file)
        self.assertEqual(results_by_file["02_consistent.csv"]["status"], "consistente")

        # Valida o arquivo com colunas diferentes (deve ser consistente nas colunas comuns)
        self.assertIn("04_different_cols.csv", results_by_file)
        self.assertEqual(results_by_file["04_different_cols.csv"]["status"], "consistente")

        # Valida o arquivo inconsistente
        self.assertIn("03_inconsistent.csv", results_by_file)
        inconsistent_result = results_by_file["03_inconsistent.csv"]
        # O profiler infere 'Numérico' para '30' e '10.1'. Para o teste ser mais robusto,
        # vamos criar uma inconsistência mais óbvia (Numérico vs. Texto).
        self._create_file("03_inconsistent.csv", "id,name,value,date\n3,C,thirty,2025-01-03")

        # Re-executar a fase
        run_discovery_phase(self.test_dir, extra_args, extensions=['csv'])

        with open(report_path, 'r', encoding='utf-8') as f:
            report_data = json.load(f)

        analysis_results = report_data.get("detailed_results", {}).get("type_consistency_analysis", [])
        results_by_file = {res['file']: res for res in analysis_results}

        inconsistent_result = results_by_file["03_inconsistent.csv"]
        self.assertEqual(inconsistent_result["status"], "inconsistente")
        self.assertEqual(len(inconsistent_result["inconsistencies"]), 1)
        inconsistency = inconsistent_result["inconsistencies"][0]
        self.assertEqual(inconsistency["column"], "value")
        self.assertEqual(inconsistency["reference_type"], "Numérico")
        self.assertEqual(inconsistency["current_type"], "Categórico/Texto")

if __name__ == '__main__':
    unittest.main()

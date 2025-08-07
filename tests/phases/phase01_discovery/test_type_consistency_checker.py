import unittest
import tempfile
import pandas as pd
import os
import gc
import sys
import time
import json
from src.phases.phase01_discovery.phase01_orchestrator import run_discovery_logic
from src.utils import METADATA_DIR


class TestTypeConsistencyChecker(unittest.TestCase):

    def setUp(self):
        """Configura um ambiente de teste limpo antes de cada teste."""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.test_dir = self.temp_dir.name
        self._created_files = []

    def tearDown(self):
        """Remove o ambiente de teste com retry logic para Windows."""
        # Força liberação de qualquer handle remanescente
        gc.collect()
        if sys.platform.startswith('win'):
            gc.collect()

        try:
            self.temp_dir.cleanup()
        except (PermissionError, OSError) as e:
            print(f"WARNING: Cleanup failed on first attempt: {e}. Retrying...")
            # Pausa e tenta novamente, uma tática comum para problemas de handle no Windows
            time.sleep(0.5)
            try:
                self.temp_dir.cleanup()
            except Exception as final_e:
                print(f"FATAL: Cleanup failed again after retry: {final_e}")
                print(f"Locked files might be: {self._created_files}")


    def _create_file(self, filename, content):
        """Cria um arquivo com o conteúdo especificado no diretório de teste."""
        file_path = os.path.join(self.test_dir, filename)
        self._created_files.append(file_path)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)

    def _create_excel_file(self, filename, data_dict):
        """Cria um arquivo Excel com os dados fornecidos de forma segura."""
        file_path = os.path.join(self.test_dir, filename)
        self._created_files.append(file_path)
        
        df = pd.DataFrame(data_dict)
        with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
            df.to_excel(writer, index=False)
        
        del df
        gc.collect()

    def test_compare_types_for_excel_and_json(self):
        """
        Testa a funcionalidade --compare-types para arquivos Excel e JSON.
        """
        # 1. Criar arquivos de teste
        self._create_excel_file("01_ref.xlsx", {"id": [1], "user": ["user_a"], "amount": [100.5]})
        self._create_excel_file("02_consistent.xlsx", {"id": [2], "user": ["user_b"], "amount": [200.0]})
        self._create_excel_file("03_inconsistent.xlsx", {"id": [3], "user": ["user_c"], "amount": ["not a number"]})
        self._create_file("01_ref.json", '{"id": 1, "product": "A", "price": 9.99}')
        self._create_file("02_consistent.json", '{"id": 2, "product": "B", "price": 19.99}')
        self._create_file("03_inconsistent.json", '{"id": 3, "product": "C", "price": "free"}')

        # 2. Executar a fase de descoberta
        run_discovery_logic(
            data_project_path=self.test_dir,
            compare_types=True,
            report_output="json",
            extensions=['xlsx', 'json']
        )

        # 3. Ler o relatório
        report_path = os.path.join(self.test_dir, METADATA_DIR, "discovery_report.json")
        self.assertTrue(os.path.exists(report_path))
        with open(report_path, 'r', encoding='utf-8') as f:
            report_data = json.load(f)

        # 4. Validar resultados
        analysis_results = report_data.get("detailed_results", {}).get("type_consistency_analysis", [])
        self.assertEqual(len(analysis_results), 6)

        results_by_file = {res['file']: res for res in analysis_results}
        self.assertEqual(results_by_file["03_inconsistent.xlsx"]["status"], "inconsistente")
        self.assertEqual(results_by_file["03_inconsistent.json"]["status"], "inconsistente")

if __name__ == '__main__':
    unittest.main()
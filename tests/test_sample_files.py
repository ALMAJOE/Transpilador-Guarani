import sys
from pathlib import Path
import glob
import os
import unittest

ROOT_DIR = Path(__file__).resolve().parent.parent
SRC_DIR = ROOT_DIR / 'src'
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from guarani import GuaraniPipeline


class TestGuaraniSampleFiles(unittest.TestCase):
    def setUp(self):
        self.pipeline = GuaraniPipeline()
        self.samples_dir = os.path.join(os.path.dirname(__file__), 'samples')
        self.sample_files = sorted(glob.glob(os.path.join(self.samples_dir, '*.gua')))

    def test_all_sample_files_parse_and_transpile(self):
        self.assertGreaterEqual(len(self.sample_files), 10)
        for path in self.sample_files:
            with self.subTest(path=path):
                with open(path, 'r', encoding='utf-8') as file:
                    source = file.read()
                tokens = self.pipeline.lex(source)
                self.assertTrue(tokens)
                ast = self.pipeline.parse(source)
                self.assertIsNotNone(ast)
                analyzer = self.pipeline.analyze(ast)
                self.assertFalse(analyzer.errors, f'Erros semânticos em {os.path.basename(path)}: {analyzer.errors}')
                code = self.pipeline.transpile(ast, analyzer.global_scope)
                self.assertIn('print', code or '')

    def test_all_sample_files_execute(self):
        for path in self.sample_files:
            with self.subTest(path=path):
                with open(path, 'r', encoding='utf-8') as file:
                    source = file.read()
                ast = self.pipeline.parse(source)
                analyzer = self.pipeline.analyze(ast)
                self.assertFalse(analyzer.errors)
                code = self.pipeline.transpile(ast, analyzer.global_scope)
                stdout, stderr = self.pipeline.execute(code)
                self.assertEqual('', stderr.strip(), f'Erros de execução em {os.path.basename(path)}:\n{stderr}')


if __name__ == '__main__':
    unittest.main()

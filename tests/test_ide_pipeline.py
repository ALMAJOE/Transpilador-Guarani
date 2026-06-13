import sys
from pathlib import Path
import unittest

ROOT_DIR = Path(__file__).resolve().parent.parent
SRC_DIR = ROOT_DIR / 'src'
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from guarani import GuaraniPipeline


class TestGuaraniPipeline(unittest.TestCase):
    def setUp(self):
        self.pipeline = GuaraniPipeline()

    def test_lex_produces_expected_tokens(self):
        source = 'papapy x = 10\nhai x\n'
        tokens = self.pipeline.lex(source)
        self.assertTrue(any(t.type == 'TYPE_INT' for t in tokens))
        self.assertTrue(any(t.type == 'HAI' for t in tokens))
        self.assertTrue(any(t.type == 'ID' and t.value == 'x' for t in tokens))

    def test_parse_returns_ast(self):
        source = 'papapy x = 1\nhai x\n'
        ast = self.pipeline.parse(source)
        self.assertEqual(len(ast.statements), 2)
        self.assertEqual(ast.statements[0].var_name, 'x')

    def test_analyze_detects_semantic_errors(self):
        source = 'papapy x = 1\nx = "ola"\n'
        ast = self.pipeline.parse(source)
        analyzer = self.pipeline.analyze(ast)
        self.assertEqual(len(analyzer.errors), 1)
        self.assertIn('Tipo incompatível', analyzer.errors[0])

    def test_transpile_generates_python_code(self):
        source = 'papapy x = 1\nhai x\n'
        ast = self.pipeline.parse(source)
        analyzer = self.pipeline.analyze(ast)
        self.assertFalse(analyzer.errors)
        code = self.pipeline.transpile(ast, analyzer.global_scope)
        self.assertIn('x = 1', code)
        self.assertIn('print(x)', code)

    def test_execute_returns_program_output(self):
        source = 'papapy x = 1\nhai x\n'
        ast = self.pipeline.parse(source)
        analyzer = self.pipeline.analyze(ast)
        code = self.pipeline.transpile(ast, analyzer.global_scope)
        stdout, stderr = self.pipeline.execute(code)
        self.assertEqual(stderr, '')
        self.assertIn('1', stdout.strip())

    def test_parse_raises_on_syntax_error(self):
        source = 'papapy x =\n'
        with self.assertRaises(SyntaxError):
            self.pipeline.parse(source)


if __name__ == '__main__':
    unittest.main()

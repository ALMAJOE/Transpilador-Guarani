import sys
from pathlib import Path
import unittest

ROOT_DIR = Path(__file__).resolve().parent.parent
SRC_DIR = ROOT_DIR / 'src'
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from guarani import IndentLexer, build_parser, SemanticAnalyzer, Transpiler


class TestTranspiladorGuarani(unittest.TestCase):
    def test_lexical_tokens_and_indentation(self):
        source = 'papapy x = 1\njave x < 3:\n    x = x + 1\n'
        lexer = IndentLexer(source)
        tokens = lexer.all_tokens()
        self.assertTrue(any(t.type == 'INDENT' for t in tokens))
        self.assertTrue(any(t.type == 'DEDENT' for t in tokens))
        self.assertEqual(tokens[0].type, 'TYPE_INT')
        self.assertEqual(tokens[1].value, 'x')
        self.assertEqual(tokens[-1].type, 'DEDENT')

    def test_mixed_indentation_raises_error(self):
        source = 'jave x < 3:\n \tx = x + 1\n'
        with self.assertRaises(IndentationError):
            IndentLexer(source)

    def test_parser_builds_ast(self):
        source = 'papapy idade = 20\nhai idade\n'
        parser = build_parser()
        ast = parser.parse(lexer=IndentLexer(source))
        self.assertEqual(len(ast.statements), 2)
        self.assertEqual(ast.statements[0].var_name, 'idade')
        self.assertEqual(ast.statements[1].expression.name, 'idade')

    def test_semantic_analysis_detects_type_errors(self):
        source = 'papapy x = 1\nx = "ola"\n'
        parser = build_parser()
        ast = parser.parse(lexer=IndentLexer(source))
        analyzer = SemanticAnalyzer()
        analyzer.analyze(ast)
        self.assertEqual(len(analyzer.errors), 1)
        self.assertIn('Tipo incompatível', analyzer.errors[0])

    def test_transpiler_generates_python_code(self):
        source = 'papapy idade = 20\nhai idade\n'
        parser = build_parser()
        ast = parser.parse(lexer=IndentLexer(source))
        analyzer = SemanticAnalyzer()
        analyzer.analyze(ast)
        self.assertFalse(analyzer.errors)
        code = Transpiler(analyzer.global_scope).transpile(ast)
        self.assertIn('idade = 20', code)
        self.assertIn('print(idade)', code)

    def test_full_pipeline_with_sample_file(self):
        with open('teste.gua', 'r', encoding='utf-8') as f:
            source = f.read()
        lexer = IndentLexer(source)
        parser = build_parser()
        ast = parser.parse(lexer=lexer)
        analyzer = SemanticAnalyzer()
        analyzer.analyze(ast)
        self.assertFalse(analyzer.errors)
        output = Transpiler(analyzer.global_scope).transpile(ast)
        self.assertIn("print('Ola, mundo!')", output)


if __name__ == '__main__':
    unittest.main()

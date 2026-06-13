import io
import traceback
import contextlib

from .lexer import IndentLexer
from .parser import build_parser
from .semantic import SemanticAnalyzer
from .transpiler import Transpiler


class GuaraniPipeline:
    def lex(self, source):
        lexer = IndentLexer(source)
        return lexer.all_tokens()

    def parse(self, source):
        lexer = IndentLexer(source)
        parser = build_parser()
        ast = parser.parse(lexer=lexer)
        if ast is None:
            raise RuntimeError('Falha na análise sintática.')
        return ast

    def analyze(self, ast):
        analyzer = SemanticAnalyzer()
        analyzer.analyze(ast)
        return analyzer

    def transpile(self, ast, symbol_table):
        return Transpiler(symbol_table).transpile(ast)

    def execute(self, code):
        stdout = io.StringIO()
        stderr = io.StringIO()
        env = {
            '__name__': '__main__',
            '__file__': '<transpiled>',
            'input': lambda prompt='': ''
        }
        try:
            with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
                exec(code, env)
        except Exception:
            traceback.print_exc(file=stderr)
        return stdout.getvalue(), stderr.getvalue()

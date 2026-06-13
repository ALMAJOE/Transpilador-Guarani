"""Pacote `guarani` do Transpilador Guarani.

Este pacote reúne o analisador léxico, sintático, semântico e o gerador
Python em uma API reutilizável para CLI, IDE e testes.
"""

from .lexer import IndentLexer
from .parser import build_parser
from .semantic import SemanticAnalyzer
from .transpiler import Transpiler
from .pipeline import GuaraniPipeline

__all__ = [
    'IndentLexer',
    'build_parser',
    'SemanticAnalyzer',
    'Transpiler',
    'GuaraniPipeline',
]

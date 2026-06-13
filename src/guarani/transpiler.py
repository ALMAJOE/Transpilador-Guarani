"""
transpiler.py — Gerador de Código (Guarani → Python)
------------------------------------------------------
Percorre a AST validada e emite código Python equivalente.

Conversões:
  hai      → print(...)
  emoinge  → <var> = int/float/str/bool(input())
  ara      → if
  nahaniri → else
  jave     → while
  faz/jave → do-while emulado com while True + break
  guata    → for ... in range(...)
  ha       → and
  tere     → or
  nahani   → not
  true     → True
  false    → False
"""

from .parser import (
    Program, VarDecl, Assign, Print, Input,
    If, While, DoWhile, For,
    BinOp, UnaryOp, Literal, Var,
)

_BIN_OP_MAP = {
    '+': '+', '-': '-', '*': '*', '/': '/',
    '>': '>', '<': '<', '>=': '>=', '<=': '<=',
    '==': '==', '!=': '!=',
    'and': 'and', 'or': 'or',
}


class Transpiler:
    def __init__(self, symbol_table):
        self.symbol_table = symbol_table
        self.lines = []
        self.indent_level = 0

    def transpile(self, program: Program) -> str:
        self.lines.append("# Código Python gerado automaticamente pelo Transpilador Guarani")
        self.lines.append("")
        for stmt in program.statements:
            self._emit_stmt(stmt)
        return "\n".join(self.lines) + "\n"

    def _indent(self) -> str:
        return "    " * self.indent_level

    def _emit(self, line: str):
        self.lines.append(self._indent() + line)

    def _emit_block(self, statements):
        self.indent_level += 1
        if not statements:
            self._emit("pass")
        else:
            for s in statements:
                self._emit_stmt(s)
        self.indent_level -= 1

    def _emit_stmt(self, node):
        method = getattr(self, f'_emit_{type(node).__name__}')
        method(node)

    def _emit_VarDecl(self, node: VarDecl):
        self._emit(f"{node.var_name} = {self._expr(node.value)}")

    def _emit_Assign(self, node: Assign):
        self._emit(f"{node.var_name} = {self._expr(node.value)}")

    def _emit_Print(self, node: Print):
        self._emit(f"print({self._expr(node.expression)})")

    def _emit_Input(self, node: Input):
        var_type = self.symbol_table.lookup(node.var_name)
        if var_type is None:
            raise RuntimeError(f"Variável '{node.var_name}' não declarada no transpiler")
        if var_type == 'bool':
            self._emit(
                f"{node.var_name} = input().strip().lower() == 'true'"
            )
            return
        converter = 'int' if var_type == 'int' else 'float' if var_type == 'float' else 'str'
        self._emit(f"{node.var_name} = {converter}(input())")

    def _emit_If(self, node: If):
        self._emit(f"if {self._expr(node.condition)}:")
        self._emit_block(node.then_block)
        if node.else_block is not None:
            self._emit("else:")
            self._emit_block(node.else_block)

    def _emit_While(self, node: While):
        self._emit(f"while {self._expr(node.condition)}:")
        self._emit_block(node.body)

    def _emit_DoWhile(self, node: DoWhile):
        # Python não tem do-while nativo; emulamos com while True + if not cond: break
        self._emit("while True:")
        self._emit_block(node.body)
        self.indent_level += 1
        self._emit(f"if not ({self._expr(node.condition)}):")
        self.indent_level += 1
        self._emit("break")
        self.indent_level -= 2

    def _emit_For(self, node: For):
        start_code = self._expr(node.start)
        end_code   = self._expr(node.end)
        self._emit(f"for {node.var_name} in range({start_code}, ({end_code}) + 1):")
        self._emit_block(node.body)

    def _expr(self, node) -> str:
        if isinstance(node, Literal):
            if node.type_name == 'string':
                return repr(node.value)
            if node.type_name == 'bool':
                return 'True' if node.value else 'False'
            return repr(node.value)

        if isinstance(node, Var):
            return node.name

        if isinstance(node, UnaryOp):
            inner = self._expr(node.operand)
            if node.op == '-':
                return f"(-{inner})"
            if node.op == 'not':
                return f"(not {inner})"

        if isinstance(node, BinOp):
            left  = self._expr(node.left)
            right = self._expr(node.right)
            py_op = _BIN_OP_MAP[node.op]
            return f"({left} {py_op} {right})"

        raise TypeError(f"Nó de expressão desconhecido: {type(node).__name__}")


if __name__ == '__main__':
    from lexer import IndentLexer
    from parser import build_parser
    from semantic import SemanticAnalyzer

    src = (
        'papapy idade = 20\n'
        'ara idade >= 18:\n'
        '    hai "Maior"\n'
        'nahaniri:\n'
        '    hai "Menor"\n'
    )
    ast = build_parser().parse(lexer=IndentLexer(src))
    sa  = SemanticAnalyzer()
    sa.analyze(ast)
    print(Transpiler(sa.global_scope).transpile(ast))

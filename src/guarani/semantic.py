"""
semantic.py — Analisador Semântico da Linguagem Guarani
--------------------------------------------------------
- Tabela de Símbolos com escopo aninhado
- Verificação de variáveis declaradas / duplicadas
- Verificação de compatibilidade de tipos
- Suporte a: VarDecl, Assign, Print, Input, If, While, DoWhile, For
"""

from .parser import (
    Program, VarDecl, Assign, Print, Input,
    If, While, DoWhile, For,
    BinOp, UnaryOp, Literal, Var,
)


class SemanticError(Exception):
    pass


# =========================================================
# Tabela de Símbolos
# =========================================================
class SymbolTable:
    def __init__(self, parent=None):
        self.symbols = {}
        self.parent  = parent

    def declare(self, name, type_name, lineno):
        if name in self.symbols:
            raise SemanticError(
                f"[Linha {lineno}] Variável '{name}' já declarada neste escopo."
            )
        self.symbols[name] = type_name

    def lookup(self, name):
        if name in self.symbols:
            return self.symbols[name]
        if self.parent is not None:
            return self.parent.lookup(name)
        return None

    def assign_check(self, name, value_type, lineno):
        existing = self.lookup(name)
        if existing is None:
            raise SemanticError(f"[Linha {lineno}] Variável '{name}' não declarada.")
        if existing == value_type:
            return
        if existing == 'float' and value_type == 'int':
            return  # promoção numérica permitida
        raise SemanticError(
            f"[Linha {lineno}] Tipo incompatível: '{name}' é '{existing}', "
            f"mas recebeu '{value_type}'."
        )

    def flat(self):
        out = {}
        if self.parent:
            out.update(self.parent.flat())
        out.update(self.symbols)
        return out


# =========================================================
# Analisador Semântico
# =========================================================
class SemanticAnalyzer:
    NUMERIC = ('int', 'float')

    def __init__(self):
        self.global_scope = SymbolTable()
        self.errors = []

    def analyze(self, program: Program):
        self._visit_block(program.statements, self.global_scope)
        return self.global_scope

    def _visit_block(self, statements, scope):
        for stmt in statements:
            try:
                self._visit(stmt, scope)
            except SemanticError as e:
                self.errors.append(str(e))

    def _visit(self, node, scope):
        method = getattr(self, f'_visit_{type(node).__name__}', None)
        if method is None:
            raise SemanticError(f"Nó não suportado: {type(node).__name__}")
        return method(node, scope)

    # ---- comandos ----

    def _visit_VarDecl(self, node: VarDecl, scope: SymbolTable):
        value_type = self._type_of(node.value, scope)
        if node.type_name != value_type:
            if not (node.type_name == 'float' and value_type == 'int'):
                raise SemanticError(
                    f"[Linha {node.lineno}] Não é possível atribuir '{value_type}' "
                    f"à variável '{node.var_name}' do tipo '{node.type_name}'."
                )
        scope.declare(node.var_name, node.type_name, node.lineno)

    def _visit_Assign(self, node: Assign, scope: SymbolTable):
        value_type = self._type_of(node.value, scope)
        scope.assign_check(node.var_name, value_type, node.lineno)

    def _visit_Print(self, node: Print, scope: SymbolTable):
        self._type_of(node.expression, scope)

    def _visit_Input(self, node: Input, scope: SymbolTable):
        if scope.lookup(node.var_name) is None:
            raise SemanticError(
                f"[Linha {node.lineno}] Variável '{node.var_name}' usada em "
                f"'emoinge' não foi declarada."
            )

    def _visit_If(self, node: If, scope: SymbolTable):
        cond_type = self._type_of(node.condition, scope)
        if cond_type != 'bool':
            raise SemanticError(
                f"[Linha {node.lineno}] Condição do 'ara' deve ser booleana, "
                f"recebida '{cond_type}'."
            )
        self._visit_block(node.then_block, SymbolTable(parent=scope))
        if node.else_block is not None:
            self._visit_block(node.else_block, SymbolTable(parent=scope))

    def _visit_While(self, node: While, scope: SymbolTable):
        cond_type = self._type_of(node.condition, scope)
        if cond_type != 'bool':
            raise SemanticError(
                f"[Linha {node.lineno}] Condição do 'jave' deve ser booleana, "
                f"recebida '{cond_type}'."
            )
        self._visit_block(node.body, SymbolTable(parent=scope))

    def _visit_DoWhile(self, node: DoWhile, scope: SymbolTable):
        self._visit_block(node.body, SymbolTable(parent=scope))
        cond_type = self._type_of(node.condition, scope)
        if cond_type != 'bool':
            raise SemanticError(
                f"[Linha {node.lineno}] Condição do 'faz...jave' deve ser "
                f"booleana, recebida '{cond_type}'."
            )

    def _visit_For(self, node: For, scope: SymbolTable):
        start_t = self._type_of(node.start, scope)
        end_t   = self._type_of(node.end, scope)
        if start_t != 'int' or end_t != 'int':
            raise SemanticError(
                f"[Linha {node.lineno}] Limites do 'guata' devem ser inteiros "
                f"(recebidos '{start_t}' e '{end_t}')."
            )
        body_scope = SymbolTable(parent=scope)
        body_scope.declare(node.var_name, 'int', node.lineno)
        self._visit_block(node.body, body_scope)

    # ---- inferência de tipos ----

    def _type_of(self, node, scope: SymbolTable) -> str:
        if isinstance(node, Literal):
            return node.type_name

        if isinstance(node, Var):
            t = scope.lookup(node.name)
            if t is None:
                raise SemanticError(
                    f"[Linha {node.lineno}] Variável '{node.name}' não declarada."
                )
            return t

        if isinstance(node, UnaryOp):
            inner = self._type_of(node.operand, scope)
            if node.op == '-':
                if inner not in self.NUMERIC:
                    raise SemanticError(
                        f"[Linha {node.lineno}] Operador '-' unário exige "
                        f"tipo numérico, recebido '{inner}'."
                    )
                return inner
            if node.op == 'not':
                if inner != 'bool':
                    raise SemanticError(
                        f"[Linha {node.lineno}] 'nahani' exige operando "
                        f"booleano, recebido '{inner}'."
                    )
                return 'bool'

        if isinstance(node, BinOp):
            lt = self._type_of(node.left, scope)
            rt = self._type_of(node.right, scope)
            op = node.op

            if op in ('+', '-', '*', '/'):
                if op == '+' and lt == 'string' and rt == 'string':
                    return 'string'
                if lt in self.NUMERIC and rt in self.NUMERIC:
                    if op == '/':
                        return 'float'
                    return 'float' if 'float' in (lt, rt) else 'int'
                raise SemanticError(
                    f"[Linha {node.lineno}] Operador '{op}' não suportado "
                    f"entre '{lt}' e '{rt}'."
                )

            if op in ('>', '<', '>=', '<=', '==', '!='):
                if lt == rt or (lt in self.NUMERIC and rt in self.NUMERIC):
                    return 'bool'
                raise SemanticError(
                    f"[Linha {node.lineno}] Comparação '{op}' inválida "
                    f"entre '{lt}' e '{rt}'."
                )

            if op in ('and', 'or'):
                if lt == 'bool' and rt == 'bool':
                    return 'bool'
                raise SemanticError(
                    f"[Linha {node.lineno}] Operador '{op}' exige booleanos, "
                    f"recebidos '{lt}' e '{rt}'."
                )

        raise SemanticError(f"Expressão desconhecida: {type(node).__name__}")


if __name__ == '__main__':
    from lexer import IndentLexer
    from parser import build_parser

    src = (
        'papapy idade = 20\n'
        'idade = "Jose"\n'
    )
    ast = build_parser().parse(lexer=IndentLexer(src))
    sa = SemanticAnalyzer()
    sa.analyze(ast)
    for err in sa.errors:
        print(err)

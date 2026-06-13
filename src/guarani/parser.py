"""
parser.py — Analisador Sintático da Linguagem Guarani
------------------------------------------------------
Gramática SEM recursividade à esquerda e SEM produções vazias.

A hierarquia de expressões segue a precedência clássica
(da menor para a maior prioridade):

  expression   → or_expr
  or_expr      → and_expr OR or_expr          (direita)
               | and_expr
  and_expr     → not_expr AND and_expr         (direita)
               | not_expr
  not_expr     → NOT not_expr
               | rel_expr
  rel_expr     → add_expr REL add_expr         (não-associativo)
               | add_expr
  add_expr     → mul_expr add_rest
  add_rest     → PLUS  mul_expr add_rest       (esquerda via recursão à direita)
               | MINUS mul_expr add_rest
               | ε   ← substituída por: sem produção vazia, usamos regra separada
  mul_expr     → unary mul_rest
  mul_rest     → TIMES  unary mul_rest
               | DIVIDE unary mul_rest
               | ε  ← idem
  unary        → MINUS unary
               | atom
  atom         → INT | FLOAT | STRING | TRUE | FALSE | ID | '(' expression ')'

Como PLY é LALR(1) (não LL), a recursividade à esquerda seria preferida
para listas, MAS o enunciado exige ausência dela. Usamos, portanto,
recursão à *direita* nas regras de lista de comandos e nas regras de
adição/multiplicação, factorizando à esquerda onde necessário.

Produções "vazias" eliminadas:
  - add_rest / mul_rest: em vez de add_rest → ε, criamos duas variantes
    de add_expr: uma que possui rest e outra que não possui.
  - statement_list: em vez de list → ε | list stmt, usamos list → stmt | stmt list
    (recursão à direita).
"""

import ply.yacc as yacc
from .lexer import tokens  # noqa: F401


# =========================================================
# Nós da AST
# =========================================================
class Node:
    pass

class Program(Node):
    def __init__(self, statements):
        self.statements = statements
    def __repr__(self):
        return f"Program({self.statements!r})"

class VarDecl(Node):
    def __init__(self, type_name, var_name, value, lineno):
        self.type_name = type_name
        self.var_name  = var_name
        self.value     = value
        self.lineno    = lineno
    def __repr__(self):
        return f"VarDecl({self.type_name}, {self.var_name}, {self.value!r})"

class Assign(Node):
    def __init__(self, var_name, value, lineno):
        self.var_name = var_name
        self.value    = value
        self.lineno   = lineno
    def __repr__(self):
        return f"Assign({self.var_name}, {self.value!r})"

class Print(Node):
    def __init__(self, expression, lineno):
        self.expression = expression
        self.lineno     = lineno
    def __repr__(self):
        return f"Print({self.expression!r})"

class Input(Node):
    def __init__(self, var_name, lineno):
        self.var_name = var_name
        self.lineno   = lineno
    def __repr__(self):
        return f"Input({self.var_name})"

class If(Node):
    def __init__(self, condition, then_block, else_block, lineno):
        self.condition  = condition
        self.then_block = then_block
        self.else_block = else_block
        self.lineno     = lineno
    def __repr__(self):
        return f"If({self.condition!r}, then={self.then_block!r}, else={self.else_block!r})"

class While(Node):
    def __init__(self, condition, body, lineno):
        self.condition = condition
        self.body      = body
        self.lineno    = lineno
    def __repr__(self):
        return f"While({self.condition!r}, {self.body!r})"

class DoWhile(Node):
    """faz: <bloco> jave <condição>  →  do { <bloco> } while (<condição>)"""
    def __init__(self, body, condition, lineno):
        self.body      = body
        self.condition = condition
        self.lineno    = lineno
    def __repr__(self):
        return f"DoWhile({self.body!r}, {self.condition!r})"

class For(Node):
    def __init__(self, var_name, start, end, body, lineno):
        self.var_name = var_name
        self.start    = start
        self.end      = end
        self.body     = body
        self.lineno   = lineno
    def __repr__(self):
        return f"For({self.var_name}, {self.start!r}, {self.end!r}, {self.body!r})"

class BinOp(Node):
    def __init__(self, op, left, right, lineno):
        self.op    = op
        self.left  = left
        self.right = right
        self.lineno = lineno
    def __repr__(self):
        return f"BinOp({self.op}, {self.left!r}, {self.right!r})"

class UnaryOp(Node):
    def __init__(self, op, operand, lineno):
        self.op      = op
        self.operand = operand
        self.lineno  = lineno
    def __repr__(self):
        return f"UnaryOp({self.op}, {self.operand!r})"

class Literal(Node):
    def __init__(self, type_name, value, lineno):
        self.type_name = type_name
        self.value     = value
        self.lineno    = lineno
    def __repr__(self):
        return f"Literal({self.type_name}, {self.value!r})"

class Var(Node):
    def __init__(self, name, lineno):
        self.name   = name
        self.lineno = lineno
    def __repr__(self):
        return f"Var({self.name})"


# =========================================================
# Precedência declarada no PLY (para resolver conflitos S/R
# residuais — não substitui a hierarquia da gramática, apenas
# desambigua casos que o LALR não consegue resolver pela
# gramática pura).
# =========================================================
precedence = ()   # a hierarquia é feita pela gramática; sem atalhos


# =========================================================
# Gramática — SEM recursão à esquerda, SEM produções vazias
# =========================================================

# ----- programa -----
def p_program(p):
    """program : statement_list"""
    p[0] = Program(p[1])

# ----- lista de comandos (recursão à DIREITA) -----
def p_statement_list_single(p):
    """statement_list : statement"""
    p[0] = [p[1]]

def p_statement_list_multiple(p):
    """statement_list : statement statement_list"""
    p[0] = [p[1]] + p[2]

# ----- comando -----
def p_statement_simple(p):
    """statement : simple_statement NEWLINE"""
    p[0] = p[1]

def p_statement_compound(p):
    """statement : compound_statement"""
    p[0] = p[1]

def p_simple_statement(p):
    """simple_statement : var_decl
                        | assignment
                        | print_stmt
                        | input_stmt"""
    p[0] = p[1]

def p_compound_statement(p):
    """compound_statement : if_stmt
                          | while_stmt
                          | dowhile_stmt
                          | for_stmt"""
    p[0] = p[1]

# ----- declaração de variável -----
_TYPE_MAP = {
    'TYPE_INT':    'int',
    'TYPE_FLOAT':  'float',
    'TYPE_STRING': 'string',
    'TYPE_BOOL':   'bool',
}

def p_var_decl(p):
    """var_decl : TYPE_INT    ID ASSIGN expression
                | TYPE_FLOAT  ID ASSIGN expression
                | TYPE_STRING ID ASSIGN expression
                | TYPE_BOOL   ID ASSIGN expression"""
    p[0] = VarDecl(_TYPE_MAP[p.slice[1].type], p[2], p[4], p.lineno(1))

# ----- atribuição -----
def p_assignment(p):
    """assignment : ID ASSIGN expression"""
    p[0] = Assign(p[1], p[3], p.lineno(1))

# ----- print -----
def p_print(p):
    """print_stmt : HAI expression"""
    p[0] = Print(p[2], p.lineno(1))

# ----- input -----
def p_input(p):
    """input_stmt : EMOINGE ID"""
    p[0] = Input(p[2], p.lineno(1))

# ----- if / if-else -----
def p_if_simple(p):
    """if_stmt : ARA expression COLON NEWLINE block"""
    p[0] = If(p[2], p[5], None, p.lineno(1))

def p_if_else(p):
    """if_stmt : ARA expression COLON NEWLINE block NAHANIRI COLON NEWLINE block"""
    p[0] = If(p[2], p[5], p[9], p.lineno(1))

# ----- while -----
def p_while(p):
    """while_stmt : JAVE expression COLON NEWLINE block"""
    p[0] = While(p[2], p[5], p.lineno(1))

# ----- do-while  (faz: <bloco> jave <condição>) -----
# Sintaxe:
#   faz:
#       <comandos>
#   jave <condição>
def p_dowhile(p):
    """dowhile_stmt : FAZ COLON NEWLINE block JAVE expression NEWLINE"""
    p[0] = DoWhile(p[4], p[6], p.lineno(1))

# ----- for -----
def p_for(p):
    """for_stmt : GUATA ID ASSIGN expression ATE expression COLON NEWLINE block"""
    p[0] = For(p[2], p[4], p[6], p[9], p.lineno(1))

# ----- bloco indentado -----
def p_block(p):
    """block : INDENT statement_list DEDENT"""
    p[0] = p[2]


# =========================================================
# Expressões — hierarquia SEM recursão à esquerda
# =========================================================
#
# Regra geral: para uma lista de operadores associativos à esquerda
# sem recursão à esquerda, usamos:
#
#   add_expr  → mul_expr add_tail
#   add_tail  → PLUS  mul_expr add_tail
#             | MINUS mul_expr add_tail
#             | mul_expr          ← produção VAZIA eliminada assim:
#
# Para eliminar ε de add_tail, fazemos:
#   add_expr  → mul_expr add_tail   (quando há tail)
#             | mul_expr            (sem tail)
#   add_tail  → PLUS  mul_expr add_tail
#             | PLUS  mul_expr
#             | MINUS mul_expr add_tail
#             | MINUS mul_expr
#
# O mesmo padrão se aplica a mul_expr / mul_tail e or_expr / and_expr.
# As ações semânticas reconstroem a árvore com associatividade à esquerda
# passando o "acumulador" como parâmetro via função auxiliar.
#
# Para simplificar as ações e manter o código legível, usamos uma
# função build_left que recebe (left, [(op, right), ...]) e constrói
# a cadeia de BinOp associativa à esquerda.
#
# A árvore é construída com associatividade à esquerda mesmo com a
# gramática sendo recursiva à direita: a tail retorna uma lista de
# (op, node) que é processada da esquerda para a direita.

def _build_left(left, tail, lineno):
    """Constrói BinOps com associatividade à esquerda a partir de uma lista [(op, right)]."""
    node = left
    for op, right in tail:
        node = BinOp(op, node, right, lineno)
    return node

# ---- expression = or_expr ----
def p_expression(p):
    """expression : or_expr"""
    p[0] = p[1]

# ---- or_expr (recursão à direita) ----
def p_or_expr_op(p):
    """or_expr : and_expr OR or_expr"""
    p[0] = BinOp('or', p[1], p[3], p.lineno(2))

def p_or_expr_pass(p):
    """or_expr : and_expr"""
    p[0] = p[1]

# ---- and_expr ----
def p_and_expr_op(p):
    """and_expr : not_expr AND and_expr"""
    p[0] = BinOp('and', p[1], p[3], p.lineno(2))

def p_and_expr_pass(p):
    """and_expr : not_expr"""
    p[0] = p[1]

# ---- not_expr ----
def p_not_expr_op(p):
    """not_expr : NOT not_expr"""
    p[0] = UnaryOp('not', p[2], p.lineno(1))

def p_not_expr_pass(p):
    """not_expr : rel_expr"""
    p[0] = p[1]

# ---- rel_expr (não-associativo) ----
def p_rel_expr_gt(p):
    """rel_expr : add_expr GT add_expr"""
    p[0] = BinOp('>', p[1], p[3], p.lineno(2))

def p_rel_expr_lt(p):
    """rel_expr : add_expr LT add_expr"""
    p[0] = BinOp('<', p[1], p[3], p.lineno(2))

def p_rel_expr_ge(p):
    """rel_expr : add_expr GE add_expr"""
    p[0] = BinOp('>=', p[1], p[3], p.lineno(2))

def p_rel_expr_le(p):
    """rel_expr : add_expr LE add_expr"""
    p[0] = BinOp('<=', p[1], p[3], p.lineno(2))

def p_rel_expr_eq(p):
    """rel_expr : add_expr EQ add_expr"""
    p[0] = BinOp('==', p[1], p[3], p.lineno(2))

def p_rel_expr_ne(p):
    """rel_expr : add_expr NE add_expr"""
    p[0] = BinOp('!=', p[1], p[3], p.lineno(2))

def p_rel_expr_pass(p):
    """rel_expr : add_expr"""
    p[0] = p[1]

# ---- add_expr ----
# add_expr → mul_expr add_tail | mul_expr
# add_tail → (PLUS|MINUS) mul_expr add_tail | (PLUS|MINUS) mul_expr
# Ação: add_tail retorna lista [(op, node), ...]

def p_add_expr_with_tail(p):
    """add_expr : mul_expr add_tail"""
    p[0] = _build_left(p[1], p[2], p[1].lineno if hasattr(p[1], 'lineno') else 0)

def p_add_expr_no_tail(p):
    """add_expr : mul_expr"""
    p[0] = p[1]

def p_add_tail_plus_more(p):
    """add_tail : PLUS mul_expr add_tail"""
    p[0] = [('+', p[2])] + p[3]

def p_add_tail_plus_end(p):
    """add_tail : PLUS mul_expr"""
    p[0] = [('+', p[2])]

def p_add_tail_minus_more(p):
    """add_tail : MINUS mul_expr add_tail"""
    p[0] = [('-', p[2])] + p[3]

def p_add_tail_minus_end(p):
    """add_tail : MINUS mul_expr"""
    p[0] = [('-', p[2])]

# ---- mul_expr ----
def p_mul_expr_with_tail(p):
    """mul_expr : unary mul_tail"""
    p[0] = _build_left(p[1], p[2], p[1].lineno if hasattr(p[1], 'lineno') else 0)

def p_mul_expr_no_tail(p):
    """mul_expr : unary"""
    p[0] = p[1]

def p_mul_tail_times_more(p):
    """mul_tail : TIMES unary mul_tail"""
    p[0] = [('*', p[2])] + p[3]

def p_mul_tail_times_end(p):
    """mul_tail : TIMES unary"""
    p[0] = [('*', p[2])]

def p_mul_tail_divide_more(p):
    """mul_tail : DIVIDE unary mul_tail"""
    p[0] = [('/', p[2])] + p[3]

def p_mul_tail_divide_end(p):
    """mul_tail : DIVIDE unary"""
    p[0] = [('/', p[2])]

# ---- unary ----
def p_unary_minus(p):
    """unary : MINUS unary"""
    p[0] = UnaryOp('-', p[2], p.lineno(1))

def p_unary_pass(p):
    """unary : atom"""
    p[0] = p[1]

# ---- atom ----
def p_atom_int(p):
    """atom : INT"""
    p[0] = Literal('int', p[1], p.lineno(1))

def p_atom_float(p):
    """atom : FLOAT"""
    p[0] = Literal('float', p[1], p.lineno(1))

def p_atom_string(p):
    """atom : STRING"""
    p[0] = Literal('string', p[1], p.lineno(1))

def p_atom_true(p):
    """atom : TRUE"""
    p[0] = Literal('bool', True, p.lineno(1))

def p_atom_false(p):
    """atom : FALSE"""
    p[0] = Literal('bool', False, p.lineno(1))

def p_atom_id(p):
    """atom : ID"""
    p[0] = Var(p[1], p.lineno(1))

def p_atom_group(p):
    """atom : LPAREN expression RPAREN"""
    p[0] = p[2]


# =========================================================
# Erro sintático
# =========================================================
def p_error(p):
    if p:
        raise SyntaxError(
            f"[Erro Sintático] Token inesperado '{p.value}' "
            f"(tipo {p.type}) na linha {p.lineno}"
        )
    raise SyntaxError('[Erro Sintático] Fim de arquivo inesperado')


# =========================================================
# Construção
# =========================================================
def build_parser():
    return yacc.yacc(debug=False, write_tables=False)


if __name__ == '__main__':
    from lexer import IndentLexer
    src = (
        'papapy idade = 20\n'
        'ara idade >= 18:\n'
        '    hai "Maior"\n'
        'nahaniri:\n'
        '    hai "Menor"\n'
    )
    ast = build_parser().parse(lexer=IndentLexer(src))
    print(ast)

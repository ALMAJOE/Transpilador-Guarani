"""
lexer.py — Analisador Léxico da Linguagem Guarani
--------------------------------------------------
Reconhece tokens, palavras reservadas e trata indentação
ao estilo Python (INDENT / DEDENT / NEWLINE).

Tipos suportados  : papapy (int), kuatia (float), nheeng (string), anhete (bool)
Estruturas de controle: ara/nahaniri (if/else)
Estruturas de repetição: jave (while), guata/ate (for), japo/jave (do-while)
Booleanos: anete (true), jasuka (false)
"""

import ply.lex as lex

# =========================================================
# Palavras reservadas
# =========================================================
reserved = {
    # tipos
    'papapy':   'TYPE_INT',
    'kuatia':   'TYPE_FLOAT',
    'nheeng':   'TYPE_STRING',
    'anhete':   'TYPE_BOOL',
    # comandos
    'hai':      'HAI',       # print
    'emoinge':  'EMOINGE',   # input
    # controle
    'ara':      'ARA',       # if
    'nahaniri': 'NAHANIRI',  # else
    # repetição
    'jave':     'JAVE',      # while  /  final do do-while
    'guata':    'GUATA',     # for
    'ate':      'ATE',       # limite superior do for
    'japo':       'FAZ',       # do  (início do do-while)
    # booleanos
    'ha':         'AND',
    'tere':       'OR',
    'nahani':     'NOT',
    'mante':     'TRUE',
    'jasuka':    'FALSE',
}

# =========================================================
# Lista de tokens
# =========================================================
tokens = [
    'INT', 'FLOAT', 'STRING', 'ID',
    'PLUS', 'MINUS', 'TIMES', 'DIVIDE',
    'GT', 'LT', 'GE', 'LE', 'EQ', 'NE',
    'ASSIGN', 'LPAREN', 'RPAREN', 'COLON',
    'NEWLINE', 'INDENT', 'DEDENT',
] + list(set(reserved.values()))

# =========================================================
# Regras simples
# =========================================================
t_PLUS   = r'\+'
t_MINUS  = r'-'
t_TIMES  = r'\*'
t_DIVIDE = r'/'
t_GE     = r'>='
t_LE     = r'<='
t_EQ     = r'=='
t_NE     = r'!='
t_GT     = r'>'
t_LT     = r'<'
t_ASSIGN = r'='
t_LPAREN = r'\('
t_RPAREN = r'\)'
t_COLON  = r':'

def t_FLOAT(t):
    r'\d+\.\d+'
    t.value = float(t.value)
    return t

def t_INT(t):
    r'\d+'
    t.value = int(t.value)
    return t

def t_STRING(t):
    r'\"([^\\\n]|(\\.))*?\"'
    t.value = t.value[1:-1]
    return t

def t_ID(t):
    r'[a-zA-Z_][a-zA-Z_0-9]*'
    t.type = reserved.get(t.value, 'ID')
    return t

def t_COMMENT(t):
    r'\#.*'
    pass

t_ignore = ' \t'

def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)
    t.type = 'NEWLINE'
    return t

def t_error(t):
    print(f"[Erro Léxico] Caractere ilegal '{t.value[0]}' na linha {t.lineno}")
    t.lexer.skip(1)

def build_lexer():
    return lex.lex()

# =========================================================
# Wrapper de indentação
# =========================================================
class IndentLexer:
    def __init__(self, source: str):
        self.tokens_list = self._tokenize(source)
        self.pos = 0

    def token(self):
        if self.pos < len(self.tokens_list):
            tok = self.tokens_list[self.pos]
            self.pos += 1
            return tok
        return None

    def all_tokens(self):
        return list(self.tokens_list)

    def _tokenize(self, source: str):
        result = []
        indent_stack = [0]
        lines = source.split('\n')
        line_no = 0
        for raw_line in lines:
            line_no += 1
            stripped = raw_line.lstrip(' \t')
            if stripped == '' or stripped.startswith('#'):
                continue
            indent_part = raw_line[:len(raw_line) - len(stripped)]
            if ' ' in indent_part and '\t' in indent_part:
                raise IndentationError(
                    f"Indentação mista (tabs + espaços) na linha {line_no}"
                )
            indent = 0
            for ch in indent_part:
                if ch == ' ':
                    indent += 1
                elif ch == '\t':
                    indent += 4
            if indent > indent_stack[-1]:
                indent_stack.append(indent)
                result.append(self._make_tok('INDENT', None, line_no))
            else:
                while indent < indent_stack[-1]:
                    indent_stack.pop()
                    result.append(self._make_tok('DEDENT', None, line_no))
                if indent != indent_stack[-1]:
                    raise IndentationError(f"Indentação inconsistente na linha {line_no}")
            base = build_lexer()
            base.input(stripped)
            base.lineno = line_no
            while True:
                tok = base.token()
                if not tok:
                    break
                if tok.type == 'NEWLINE':
                    continue
                result.append(tok)
            result.append(self._make_tok('NEWLINE', None, line_no))
        while len(indent_stack) > 1:
            indent_stack.pop()
            result.append(self._make_tok('DEDENT', None, line_no))
        return result

    @staticmethod
    def _make_tok(ttype, value, lineno):
        tok = lex.LexToken()
        tok.type  = ttype
        tok.value = value
        tok.lineno = lineno
        tok.lexpos = 0
        return tok

if __name__ == '__main__':
    exemplo = 'papapy idade = 20\n'
    il = IndentLexer(exemplo)
    for tk in il.all_tokens():
        print(f"  {tk.type:12s} {tk.value!r}")

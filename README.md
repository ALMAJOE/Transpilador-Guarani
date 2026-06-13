# GuaCode (Transpilador Guarani)

**Linguagem de Programação Guarani → Python**

Transpilador completo (léxico, sintático, semântico e geração de código) com **CLI** e **IDE gráfica própria**, desenvolvido para a disciplina de **Teoria da Computação e Compiladores**.

- **Professor:** Eduardo Xavier
- **Curso:** Ciência da Computação
- **Matéria:** Teoria da Computação e Compiladores
- **Instituição:** UNIFACS — Universidade Salvador
- **Linguagem usada:** Python 3
- **Biblioteca principal:** PLY (Python Lex-Yacc)

---

## Autores do projeto

> - Enzo Rosa Reis - 12724130547
> - José Almiro Lima dos Santos - 12724161839
> - Mateus Moreira de Oliveira Andrade - 12724114040
> - Vinícius Ariel Ribeiro dos Santos - 1272318365
> - Pedro Carneiro - 12723131027

---

## Sumário

1. [Visão Geral](#1-visão-geral)
2. [A Linguagem Guarani](#2-a-linguagem-guarani)
3. [Tecnologias Utilizadas](#3-tecnologias-utilizadas)
4. [Arquitetura e Pipeline](#4-arquitetura-e-pipeline)
5. [Estrutura do Projeto](#5-estrutura-do-projeto)
6. [Instalação](#6-instalação)
7. [Como Executar](#7-como-executar)
8. [A IDE GuaCode](#8-a-ide-guarani)
9. [Referência da Linguagem](#9-referência-da-linguagem)
10. [Análise Léxica — `lexer.py`](#10-análise-léxica--lexerpy)
11. [Análise Sintática — `parser.py`](#11-análise-sintática--parserpy)
12. [Análise Semântica — `semantic.py`](#12-análise-semântica--semanticpy)
13. [Geração de Código — `transpiler.py`](#13-geração-de-código--transpilerpy)
14. [Exemplo Completo](#14-exemplo-completo)
15. [Testes](#15-testes)
16. [Conceitos de Compiladores Aplicados](#16-conceitos-de-compiladores-aplicados)
17. [Conclusão](#17-conclusão)

---

## 1. Visão Geral

O GuaCode é uma linguagem de programação com foco na didática que foi diretamente inspirada pelo idioma nativo de terras da América do Sul, mais especificamente do Paraguai e às regiões Sul, Sudeste e Centro-Oeste do Brasil.

Outrossim, as palavras reservadas do GuaCode são todas inspiradas em termos do Guarani, de modo a inserir estes termos onde ocorreriam aparições de itens naturais das lingugagens tradicionais de programação, como, por exemplo, o termo Guarani `papapy` para inteiro, `hai` para imprimir, `ara` para condicional, e assim por diante.

O transpilador lê um arquivo em nossa extensão, `.gua`, e executa as quatro etapas clássicas de um compilador, a **análise léxica**, **análise sintática**, **análise semântica** e **geração de código**, ao final, produzindo um arquivo Python equivalente, pronto para execução.

Diferente de um compilador tradicional, que gera código de máquina ou bytecode, este projeto realiza uma **transpilação**, a transpilação traduz código de uma linguagem de alto nível (Guarani) para outra linguagem de alto nível (Python), preservando a semântica do programa original.

O projeto oferece **duas principais formas de uso**:

- **Linha de comando (CLI)** — `main.py`, ideal para automação e depuração etapa por etapa.
- **IDE gráfica (Tkinter)** — `ide.py`, com editor de código, visualização de tokens, AST, código Python gerado, execução integrada e logs.

Ambas as interfaces compartilham o mesmo núcleo de transpilação através do pacote reutilizável `guarani`.

---

## 2. A Linguagem Guarani

A ideia por trás da linguagem e da criação do GuaCode é tornar o aprendizado de compiladores mais acessível e culturalmente conectado, substituindo palavras-chave inglesas por termos Guarani, de modo que o código se parece com pseudocódigo natural, mas é totalmente formal e verificável.

**Exemplo mínimo:**

```guarani
papapy idade = 20

ara idade >= 18:
    hai "Maior de idade"
nahaniri:
    hai "Menor de idade"
```

**Python gerado:**

```python
idade = 20
if (idade >= 18):
    print('Maior de idade')
else:
    print('Menor de idade')
```

Os blocos são delimitados por **indentação** (ao estilo Python), e não por chaves. O analisador léxico gera tokens especiais `INDENT`, `DEDENT` e `NEWLINE` para representar essa estrutura.

---

## 3. Tecnologias Utilizadas

| Recurso | Uso no projeto |
|---|---|
| **Python 3** | Linguagem de implementação |
| **PLY (Python Lex-Yacc)** | Geração do analisador léxico (lex) e sintático LALR(1) (yacc) |
| **Tkinter** | Interface gráfica da IDE (parte da biblioteca padrão) |
| **unittest** | Suíte de testes automatizados |
| **argparse** | Interface de linha de comando |
| **dataclasses / typing** | Estruturas auxiliares e legibilidade |

### Paradigmas e conceitos aplicados

- Programação Orientada a Objetos (nós da AST, tabela de símbolos, pipeline)
- Análise léxica baseada em expressões regulares
- Gramática livre de contexto **sem recursão à esquerda** e **sem produções vazias (ε)**
- Árvore Sintática Abstrata (AST)
- Tabela de símbolos com escopos aninhados
- Verificação e inferência de tipos
- Geração de código e execução dinâmica isolada (sandbox)

---

## 4. Arquitetura e Pipeline

O sistema é dividido em módulos independentes, organizados em um **pipeline** unificado (`GuaraniPipeline`) consumido tanto pela CLI quanto pela IDE.

```
                       ┌──────────────────────────┐
                       │   Código-fonte (.gua)     │
                       └────────────┬─────────────┘
                                    ↓
                       ┌──────────────────────────┐
                       │  Lexer (IndentLexer)      │   lexer.py
                       │  Texto → Tokens           │
                       │  + INDENT/DEDENT/NEWLINE  │
                       └────────────┬─────────────┘
                                    ↓
                       ┌──────────────────────────┐
                       │  Parser (PLY / LALR(1))   │   parser.py
                       │  Tokens → AST             │
                       └────────────┬─────────────┘
                                    ↓
                       ┌──────────────────────────┐
                       │  Analisador Semântico     │   semantic.py
                       │  Tabela de símbolos       │
                       │  Verificação de tipos     │
                       └────────────┬─────────────┘
                                    ↓
                       ┌──────────────────────────┐
                       │  Transpilador             │   transpiler.py
                       │  AST → Código Python      │
                       └────────────┬─────────────┘
                                    ↓
              ┌─────────────────────┴─────────────────────┐
              ↓                                             ↓
   ┌────────────────────┐                       ┌────────────────────┐
   │  Arquivo output.py │                       │  Execução dinâmica │
   │  (gerado em disco) │                       │  (exec sandbox)    │
   └────────────────────┘                       └────────────────────┘
```

O orquestrador `GuaraniPipeline` (em `pipeline.py`) expõe métodos isolados — `lex()`, `parse()`, `analyze()`, `transpile()` e `execute()` — permitindo executar qualquer etapa de forma independente. É exatamente isso que torna a IDE capaz de mostrar tokens, AST e código separadamente.

---

## 5. Estrutura do Projeto

```plaintext
Transpilador-Guarani/
│
├── src/
│   ├── guarani/                 # Pacote principal (núcleo reutilizável)
│   │   ├── __init__.py          # API pública do pacote
│   │   ├── lexer.py             # Análise léxica + IndentLexer
│   │   ├── parser.py            # Análise sintática + nós da AST
│   │   ├── semantic.py          # Análise semântica + tabela de símbolos
│   │   ├── transpiler.py        # Geração de código Python
│   │   └── pipeline.py          # Orquestrador (GuaraniPipeline)
│   │
│   ├── main.py                  # Lógica da CLI
│   └── ide.py                   # IDE gráfica (Tkinter)
│
├── tests/
│   ├── samples/                 # 10 programas .gua de exemplo
│   │   ├── arithmetic.gua
│   │   ├── assignments.gua
│   │   ├── boolean_logic.gua
│   │   ├── declarations.gua
│   │   ├── do_while.gua
│   │   ├── for_loop.gua
│   │   ├── if_else.gua
│   │   ├── nested_blocks.gua
│   │   ├── string_concat.gua
│   │   └── while.gua
│   ├── test_transpilador.py     # Testes do núcleo (lexer→transpiler)
│   ├── test_ide_pipeline.py     # Testes do GuaraniPipeline
│   └── test_sample_files.py     # Testa todos os exemplos de samples/
│
├── generated/
│   └── output.py                # Código Python gerado (saída padrão)
│
├── main.py                      # Lançador da CLI (raiz)
├── ide.py                       # Lançador da IDE (raiz)
├── teste.gua                    # Programa de teste completo
├── requirements.txt             # Dependências (ply>=3.11)
└── Guarani.docx                 # Documentação formal do projeto
```

> Os arquivos `main.py` e `ide.py` na raiz são apenas **lançadores**: configuram o `sys.path` e chamam o código real dentro de `src/`. Assim você pode rodar tudo a partir da raiz do projeto sem se preocupar com imports.

---

## 6. Instalação

### Pré-requisitos

- **Python 3.8** ou superior
- **PLY** (instalada via `pip`)
- **Tkinter** — já incluído na biblioteca padrão do Python. Em algumas distribuições Linux pode ser necessário instalar separadamente (`sudo apt install python3-tk`).

### Passos

```bash
# 1. Clonar o repositório
git clone https://github.com/ALMAJOE/Transpilador-Guarani
cd TeoriaCC-A3

# 2. Instalar a dependência
pip install -r requirements.txt
# ou, diretamente:
pip install ply
```

---

## 7. Como Executar

### 7.1 Linha de Comando (CLI)

```bash
# Transpilar (gera generated/output.py)
python main.py teste.gua

# Transpilar e executar imediatamente
python main.py teste.gua --run

# Definir nome/local do arquivo de saída
python main.py teste.gua -o saida.py

# Exibir os tokens (debug léxico)
python main.py teste.gua --tokens

# Exibir a AST (debug sintático)
python main.py teste.gua --ast
```

| Flag | Descrição |
|---|---|
| *(nenhuma)* | Transpila e grava o Python gerado |
| `-o`, `--output` | Define o caminho do arquivo `.py` de saída |
| `--run` | Executa o código Python gerado após transpilar |
| `--tokens` | Imprime a lista de tokens produzida pelo lexer |
| `--ast` | Imprime a árvore sintática abstrata |

### 7.2 IDE Gráfica

```bash
python ide.py
```

A IDE abre uma janela completa com editor, abas de visualização e execução integrada (detalhada na próxima seção).

---

## 8. A IDE GuaCode

A **GuaCode IDE** é um ambiente de desenvolvimento completo construído em Tkinter, com tema escuro inspirado em editores modernos. Ela permite escrever, depurar, transpilar e executar programas Guarani sem sair da interface.

### Abas de visualização

A IDE organiza o fluxo de transpilação em **5 abas**, atualizadas conforme você executa cada etapa:

| Aba | Conteúdo |
|---|---|
| **Código Fonte (.gua)** | Editor principal com numeração de linhas |
| **Python Gerado** | Código Python resultante da transpilação |
| **Tokens** | Lista completa de tokens (saída do lexer) |
| **Árvore (AST)** | Representação da árvore sintática abstrata |
| **Logs** | Mensagens de status, erros e saída de execução |

### Barra de ferramentas e menu

A barra superior oferece botões para cada etapa do pipeline, além de operações de arquivo:

- **Arquivo:** Abrir, Salvar, Salvar Como, Novo, Salvar Python
- **Etapas de compilação:** Lexar, Parse, Semântica, Transpilar
- **Execução:** Executar (roda o pipeline completo e mostra a saída)

### Atalhos de teclado

| Atalho | Ação |
|---|---|
| `Ctrl + O` | Abrir arquivo |
| `Ctrl + S` | Salvar |
| `Ctrl + Shift + S` | Salvar Como |
| `Ctrl + L` | Análise léxica (Lexar) |
| `Ctrl + P` | Análise sintática (Parse) |
| `Ctrl + M` | Análise semântica |
| `Ctrl + T` | Transpilar |
| `F5` | Executar |

### Recursos adicionais

- **Numeração de linhas** sincronizada com a rolagem do editor.
- **Indicador de modificação** (●) no título quando há alterações não salvas.
- **Barra de status** mostrando o estado atual (tokens gerados, linhas, erros etc.).
- **Tooltips** nos botões da barra de ferramentas.
- **Execução isolada:** o código gerado roda em um ambiente controlado com captura de `stdout`/`stderr`, evitando que erros derrubem a interface.
- **Bloqueio inteligente:** transpilação e execução são interrompidas automaticamente caso haja erros semânticos, que são listados na aba de Logs.

---

## 9. Referência da Linguagem

### 9.1 Palavras Reservadas

| Guarani | Token Interno | Equivalente em Python |
|---|---|---|
| `papapy` | `TYPE_INT` | `int` — tipo inteiro |
| `kuatia` | `TYPE_FLOAT` | `float` — tipo decimal |
| `nheeng` | `TYPE_STRING` | `str` — tipo texto |
| `anhete` | `TYPE_BOOL` | `bool` — tipo booleano |
| `hai` | `HAI` | `print` — impressão na tela |
| `emoinge` | `EMOINGE` | `input` — leitura do teclado |
| `ara` | `ARA` | `if` — condicional |
| `nahaniri` | `NAHANIRI` | `else` — senão |
| `jave` | `JAVE` | `while` / fechamento do `do-while` |
| `guata` | `GUATA` | `for` — para |
| `ate` | `ATE` | limite superior do `for` |
| `japo` | `FAZ` | `do` — início do `do-while` |
| `ha` | `AND` | `and` — e lógico |
| `tere` | `OR` | `or` — ou lógico |
| `nahani` | `NOT` | `not` — negação |
| `mante` | `TRUE` | `True` — verdadeiro |
| `jasuka` | `FALSE` | `False` — falso |

### 9.2 Outros Tokens Reconhecidos

| Token | Padrão | Descrição |
|---|---|---|
| `INT` | `\d+` | Número inteiro |
| `FLOAT` | `\d+\.\d+` | Número decimal |
| `STRING` | `"([^\\\n]\|\\.)*"` | Cadeia entre aspas duplas |
| `ID` | `[a-zA-Z_]\w*` | Identificador de variável |
| `PLUS` / `MINUS` | `+` / `-` | Adição / Subtração (e negação unária) |
| `TIMES` / `DIVIDE` | `*` / `/` | Multiplicação / Divisão |
| `GT` / `LT` | `>` / `<` | Maior que / Menor que |
| `GE` / `LE` | `>=` / `<=` | Maior ou igual / Menor ou igual |
| `EQ` / `NE` | `==` / `!=` | Igual / Diferente |
| `ASSIGN` | `=` | Atribuição |
| `COLON` | `:` | Dois-pontos (início de bloco) |
| `LPAREN` / `RPAREN` | `(` / `)` | Parênteses |
| `INDENT` | *(gerado)* | Aumento de indentação |
| `DEDENT` | *(gerado)* | Redução de indentação |
| `NEWLINE` | *(gerado)* | Fim de linha lógica |

Comentários começam com `#` e vão até o fim da linha (são ignorados pelo lexer).

### 9.3 Tipos de Dados

| Guarani | Declaração | Python gerado |
|---|---|---|
| `papapy` | `papapy idade = 20` | `idade = 20` |
| `kuatia` | `kuatia altura = 1.75` | `altura = 1.75` |
| `nheeng` | `nheeng nome = "Jose"` | `nome = 'Jose'` |
| `anhete` | `anhete ativo = mante` | `ativo = True` |
| `anhete` | `anhete inativo = jasuka` | `inativo = False` |

### 9.4 Equivalência Guarani → Python

#### Entrada e Saída

| Guarani | Python gerado |
|---|---|
| `hai "Ola, mundo!"` | `print('Ola, mundo!')` |
| `hai nome` | `print(nome)` |
| `emoinge idade` *(int)* | `idade = int(input())` |
| `emoinge altura` *(float)* | `altura = float(input())` |
| `emoinge nome` *(string)* | `nome = str(input())` |
| `emoinge ativo` *(bool)* | `ativo = input().strip().lower() == 'true'` |

> A conversão do `emoinge` é **sensível ao tipo declarado** da variável: o transpilador consulta a tabela de símbolos para escolher entre `int`, `float`, `str` ou a leitura booleana.

#### Condicional (`ara` / `nahaniri`)

```
── Guarani ──────────────────────   ── Python ──────────────────────
ara idade >= 18:                    if (idade >= 18):
    hai "Maior de idade"                print('Maior de idade')
nahaniri:                           else:
    hai "Menor de idade"                print('Menor de idade')
```

#### Repetição `while` (`jave`)

```
── Guarani ──────────────────────   ── Python ──────────────────────
jave contador < 5:                  while (contador < 5):
    hai contador                        print(contador)
    contador = contador + 1             contador = (contador + 1)
```

#### Repetição `do-while` (`japo` ... `jave`)

```
── Guarani ──────────────────────   ── Python ──────────────────────
japo:                               while True:
    hai x                               print(x)
    x = x + 1                           x = (x + 1)
jave x <= 3                             if not ((x <= 3)):
                                            break
```

#### Repetição `for` (`guata` ... `ate`)

```
── Guarani ──────────────────────   ── Python ──────────────────────
guata i = 1 ate 3:                  for i in range(1, (3) + 1):
    hai i                               print(i)
```

> O `for` da Guarani tem **limite inclusivo**: `guata i = 1 ate 3` itera sobre 1, 2 e 3. Por isso o transpilador soma `+ 1` ao limite superior no `range`.

#### Operadores

| Categoria | Guarani | Python | Descrição |
|---|---|---|---|
| Aritmético | `+` | `+` | Adição / concatenação de strings |
| Aritmético | `-` | `-` | Subtração / negação unária |
| Aritmético | `*` | `*` | Multiplicação |
| Aritmético | `/` | `/` | Divisão (sempre retorna `float`) |
| Relacional | `>` | `>` | Maior que |
| Relacional | `<` | `<` | Menor que |
| Relacional | `>=` | `>=` | Maior ou igual |
| Relacional | `<=` | `<=` | Menor ou igual |
| Relacional | `==` | `==` | Igual |
| Relacional | `!=` | `!=` | Diferente |
| Lógico | `ha` | `and` | E lógico |
| Lógico | `tere` | `or` | Ou lógico |
| Lógico | `nahani` | `not` | Negação lógica |

---

## 10. Análise Léxica — `lexer.py`

O arquivo `lexer.py` reconhece todos os tokens da linguagem usando **PLY**. Um wrapper de indentação (`IndentLexer`) processa o código linha a linha e gera os tokens especiais `INDENT`, `DEDENT` e `NEWLINE`, permitindo blocos delimitados por espaçamento ao estilo Python.

### Como funciona o `IndentLexer`

1. Quebra o código em linhas e ignora linhas em branco e comentários.
2. Para cada linha, calcula o nível de indentação (espaços contam 1, tabs contam 4).
3. Compara com o topo de uma **pilha de indentação**:
   - Indentação maior → emite `INDENT` e empilha o novo nível.
   - Indentação menor → emite `DEDENT`(s) e desempilha até alinhar.
4. Tokeniza o conteúdo da linha com o lexer base do PLY.
5. Emite um `NEWLINE` ao final de cada linha lógica.
6. Ao final do arquivo, fecha todos os blocos abertos com `DEDENT`s.

### Tratamento de erros

- **Indentação mista** (tabs + espaços na mesma linha) lança `IndentationError`.
- **Indentação inconsistente** (nível que não corresponde a nenhum da pilha) também lança `IndentationError`.
- Caracteres ilegais são reportados com a linha onde ocorreram.

**Exemplo de saída de tokens** (`python main.py mini.gua --tokens`):

```plaintext
TYPE_INT     'papapy'
ID           'idade'
ASSIGN       '='
INT          20
NEWLINE      None
ARA          'ara'
ID           'idade'
GE           '>='
INT          18
COLON        ':'
NEWLINE      None
INDENT       None
HAI          'hai'
STRING       'Maior'
NEWLINE      None
DEDENT       None
...
```

---

## 11. Análise Sintática — `parser.py`

O `parser.py` define a gramática da linguagem e constrói a **Árvore Sintática Abstrata (AST)** usando PLY (estratégia LALR(1)). Conforme exigido pelo enunciado, a gramática é **livre de recursão à esquerda** e **livre de produções vazias (ε)**.

### Nós da AST

| Nó | Campos |
|---|---|
| `Program` | `statements` |
| `VarDecl` | `type_name`, `var_name`, `value` |
| `Assign` | `var_name`, `value` |
| `Print` | `expression` |
| `Input` | `var_name` |
| `If` | `condition`, `then_block`, `else_block` |
| `While` | `condition`, `body` |
| `DoWhile` | `body`, `condition` |
| `For` | `var_name`, `start`, `end`, `body` |
| `BinOp` | `op`, `left`, `right` |
| `UnaryOp` | `op`, `operand` |
| `Literal` | `type_name`, `value` |
| `Var` | `name` |

*(Todos os nós também guardam `lineno` para mensagens de erro precisas.)*

### Gramática Completa

#### Programa e comandos

```
program            → statement_list

statement_list     → statement
                   | statement statement_list

statement          → simple_statement NEWLINE
                   | compound_statement

simple_statement   → var_decl | assignment | print_stmt | input_stmt

compound_statement → if_stmt | while_stmt | dowhile_stmt | for_stmt
```

#### Declaração, atribuição e I/O

```
var_decl    → (TYPE_INT | TYPE_FLOAT | TYPE_STRING | TYPE_BOOL) ID ASSIGN expression
assignment  → ID ASSIGN expression
print_stmt  → HAI expression
input_stmt  → EMOINGE ID
```

#### Estruturas de controle e repetição

```
if_stmt      → ARA expression COLON NEWLINE block
             | ARA expression COLON NEWLINE block NAHANIRI COLON NEWLINE block

while_stmt   → JAVE expression COLON NEWLINE block

dowhile_stmt → FAZ COLON NEWLINE block JAVE expression NEWLINE

for_stmt     → GUATA ID ASSIGN expression ATE expression COLON NEWLINE block

block        → INDENT statement_list DEDENT
```

#### Expressões — hierarquia de precedência

A precedência dos operadores, da **menor para a maior** prioridade, é:

`OR → AND → NOT → relacionais → adição/subtração → multiplicação/divisão → negação unária → átomo`

```
expression → or_expr

or_expr    → and_expr OR or_expr
           | and_expr

and_expr   → not_expr AND and_expr
           | not_expr

not_expr   → NOT not_expr
           | rel_expr

rel_expr   → add_expr (GT | LT | GE | LE | EQ | NE) add_expr
           | add_expr

add_expr   → mul_expr add_tail
           | mul_expr

add_tail   → PLUS  mul_expr add_tail
           | PLUS  mul_expr
           | MINUS mul_expr add_tail
           | MINUS mul_expr

mul_expr   → unary mul_tail
           | unary

mul_tail   → TIMES  unary mul_tail
           | TIMES  unary
           | DIVIDE unary mul_tail
           | DIVIDE unary

unary      → MINUS unary
           | atom

atom       → INT | FLOAT | STRING | TRUE | FALSE | ID
           | LPAREN expression RPAREN
```

> **Eliminação de produções vazias:** numa gramática clássica, `add_rest → ε` introduziria produções vazias. Aqui, isso é evitado criando duas variantes de cada regra de cauda (`add_tail`, `mul_tail`): uma que continua a cadeia e outra que a encerra.
>
> **Associatividade à esquerda:** embora a gramática use recursão à *direita* (para evitar recursão à esquerda), a associatividade correta dos operadores aritméticos é recuperada nas ações semânticas pela função auxiliar `_build_left`, que recebe a lista `[(op, nó), ...]` e a processa da esquerda para a direita construindo a cadeia de `BinOp`.

### Precedência demonstrada

A expressão `2 + 3 * 4` é corretamente transpilada como `(2 + (3 * 4))`, resultando em **14** (e não 20) — exatamente como em matemática e em Python.

---

## 12. Análise Semântica — `semantic.py`

O analisador semântico percorre a AST e valida a corretude do programa antes da geração de código. Ele usa uma **tabela de símbolos com escopos aninhados**, cada bloco (`ara`, `jave`, `japo`, `guata`) cria um escopo filho, e variáveis declaradas dentro de um bloco não são visíveis fora dele.

### Verificações realizadas

- Variável não pode ser usada antes de ser declarada.
- Variável não pode ser declarada duas vezes no mesmo escopo.
- O tipo do valor atribuído deve ser compatível com o tipo declarado.
- **Promoção numérica:** um `int` pode ser atribuído a uma variável `float`.
- Operadores aritméticos exigem operandos numéricos (`int` ou `float`); a exceção é `+`, que também concatena duas `string`.
- A divisão `/` sempre resulta em `float`.
- Operadores relacionais exigem operandos do mesmo tipo (ou ambos numéricos) e produzem `bool`.
- Operadores lógicos (`ha`, `tere`, `nahani`) exigem operandos booleanos.
- As condições de `ara`, `jave` e `japo...jave` devem ser do tipo `bool`.
- Os limites do `guata` (`for`) devem ser inteiros.

### Coleta de erros

Os erros não interrompem a análise imediatamente, o analisador **acumula todos os erros semânticos** em uma lista e os reporta de uma vez, com o número da linha de cada um. A CLI aborta a geração de código se houver qualquer erro, a IDE lista todos na aba de Logs.

**Exemplo de erro detectado:**

```guarani
papapy x = 1
x = "ola"
```

```
[Linha 2] Tipo incompatível: 'x' é 'int', mas recebeu 'string'.
```

---

## 13. Geração de Código — `transpiler.py`

O transpilador percorre a AST já validada e emite código Python equivalente, controlando a indentação à medida que entra e sai de blocos.

### Conversões principais

| Construção Guarani | Código Python emitido |
|---|---|
| `VarDecl` / `Assign` | `nome = <expressão>` |
| `hai` (`Print`) | `print(<expressão>)` |
| `emoinge` (`Input`) | conversão sensível ao tipo (`int`/`float`/`str`/`bool`) |
| `ara` / `nahaniri` (`If`) | `if ...:` / `else:` |
| `jave` (`While`) | `while ...:` |
| `japo...jave` (`DoWhile`) | `while True:` + `if not (cond): break` |
| `guata...ate` (`For`) | `for v in range(início, (fim) + 1):` |
| `BinOp` | `(esquerda op direita)` |
| `UnaryOp` `-` / `not` | `(-x)` / `(not x)` |

### Detalhes importantes

- **`do-while` em Python:** como Python não possui `do-while` nativo, ele é emulado com `while True` seguido de uma verificação `if not (condição): break` no final do corpo — garantindo que o bloco execute ao menos uma vez.
- **Parênteses explícitos:** todas as expressões binárias são envolvidas em parênteses, o que torna a precedência inequívoca no código gerado e dispensa qualquer ambiguidade.
- **Blocos vazios:** se um bloco não tiver comandos, o transpilador emite `pass` para manter o Python válido.

---

## 14. Exemplo Completo

### Código de teste — `teste.gua`

```guarani
# 1. Declaracao dos 4 tipos de dados
papapy idade = 20
kuatia altura = 1.75
nheeng nome = "Jose"
anhete ativo = mante

# 2. Impressao (hai = print)
hai "Ola, mundo!"
hai nome
hai idade
hai altura

# 3. Condicional (ara = if, nahaniri = else)
ara idade >= 18:
    hai "Maior de idade"
nahaniri:
    hai "Menor de idade"

# 4. while (jave)
papapy contador = 0
jave contador < 5:
    hai contador
    contador = contador + 1

# 5. for (guata ... ate)
guata i = 1 ate 3:
    hai i

# 6. do-while (japo ... jave)
papapy x = 1
japo:
    hai x
    x = x + 1
jave x <= 3

# 7. Expressao com precedencia (2 + 3 * 4 = 14, nao 20)
papapy resultado = 2 + 3 * 4
hai resultado

# 8. Operadores booleanos (ha = and, tere = or)
ara idade >= 18 ha ativo == mante:
    hai "Adulto ativo"

# 9. Exemplo com false
anhete inativo = jasuka
hai inativo

# 10. Concatenacao de strings
nheeng saudacao = "Ola, " + nome
hai saudacao
```

### Código Python gerado — `generated/output.py`

```python
# Código Python gerado automaticamente pelo GuaCode

idade = 20
altura = 1.75
nome = 'Jose'
ativo = True
print('Ola, mundo!')
print(nome)
print(idade)
print(altura)
if (idade >= 18):
    print('Maior de idade')
else:
    print('Menor de idade')
contador = 0
while (contador < 5):
    print(contador)
    contador = (contador + 1)
for i in range(1, (3) + 1):
    print(i)
x = 1
while True:
    print(x)
    x = (x + 1)
    if not ((x <= 3)):
        break
resultado = (2 + (3 * 4))
print(resultado)
if ((idade >= 18) and (ativo == True)):
    print('Adulto ativo')
inativo = False
print(inativo)
saudacao = ('Ola, ' + nome)
print(saudacao)
```

### Saída da execução

```
Ola, mundo!
Jose
20
1.75
Maior de idade
0
1
2
3
4
1
2
3
1
2
3
14
Adulto ativo
False
Ola, Jose
```

---

## 15. Testes

O projeto inclui uma suíte de **14 testes automatizados** com `unittest`, cobrindo todas as etapas do pipeline e validando os 10 programas de exemplo.

### Executar todos os testes

```bash
python -m unittest discover -s tests -v
```

### Arquivos de teste

| Arquivo | O que cobre |
|---|---|
| `test_transpilador.py` | Núcleo completo: tokens e indentação, detecção de indentação mista, construção da AST, erros de tipo, geração de código e pipeline com `teste.gua` |
| `test_ide_pipeline.py` | A API `GuaraniPipeline`: `lex`, `parse`, `analyze`, `transpile`, `execute` e erros de sintaxe |
| `test_sample_files.py` | Garante que **todos** os arquivos em `tests/samples/` transpilam e executam sem erros |

### Programas de exemplo (`tests/samples/`)

Dez programas curtos exercitam cada recurso da linguagem de forma isolada:

| Arquivo | Recurso demonstrado |
|---|---|
| `declarations.gua` | Declaração dos 4 tipos e impressão |
| `assignments.gua` | Atribuição e atualização de variáveis |
| `arithmetic.gua` | Expressões aritméticas e precedência |
| `string_concat.gua` | Concatenação de strings |
| `boolean_logic.gua` | Operadores booleanos (`ha`, `==`) |
| `if_else.gua` | Condicional com `ara` / `nahaniri` |
| `while.gua` | Laço `jave` |
| `for_loop.gua` | Laço `guata ... ate` |
| `do_while.gua` | Laço `japo ... jave` |
| `nested_blocks.gua` | Blocos aninhados (if dentro de while etc.) |

**Resultado esperado:**

```
Ran 14 tests in 0.32s

OK
```

---

## 16. Conceitos de Compiladores Aplicados

| Conceito | Implementado |
|---|---|
| Análise Léxica (Lexer) | ✅ |
| Tratamento de indentação (INDENT/DEDENT) | ✅ |
| Análise Sintática (Parser LALR(1)) | ✅ |
| Gramática sem recursão à esquerda | ✅ |
| Gramática sem produções vazias (ε) | ✅ |
| Árvore Sintática Abstrata (AST) | ✅ |
| Análise Semântica | ✅ |
| Tabela de símbolos com escopos aninhados | ✅ |
| Verificação e inferência de tipos | ✅ |
| Geração de código | ✅ |
| Execução dinâmica isolada | ✅ |
| IDE com visualização de cada etapa | ✅ |
| Suíte de testes automatizados | ✅ |

---


## 17. Desafios de Implementação e Limitações Conhecidas

Esta seção documenta as principais decisões técnicas tomadas durante o desenvolvimento, os desafios encontrados em cada etapa do pipeline e as limitações que permanecem na versão atual.

---

### 17.1 Indentação Sensível ao Contexto

**Desafio:** O PLY não oferece suporte nativo a tokens sintéticos baseados em indentação. Como a linguagem Guarani delimita blocos por indentação (ao estilo Python), foi necessário criar o `IndentLexer` — um *wrapper* que pré-processa o código fonte linha a linha, mantém uma pilha de níveis de indentação e injeta os tokens `INDENT`, `DEDENT` e `NEWLINE` manualmente antes de repassar a sequência ao parser.

**Decisão:** Construir o `IndentLexer` como uma camada separada sobre o lexer base do PLY, em vez de tentar estender as regras padrão. Isso isolou a complexidade da indentação e manteve o lexer principal simples.

**Limitação atual:** Cada linha é reprocessada por uma nova instância do lexer base, o que é funcionalmente correto mas ineficiente para arquivos grandes. Além disso, a mistura de tabs e espaços lança `IndentationError`, mas o número de espaços equivalente a um tab está fixo em 4.

---

### 17.2 Gramática sem Recursão à Esquerda e sem Produções Vazias

**Desafio:** O enunciado da disciplina exigiu que a gramática fosse escrita sem recursão à esquerda e sem produções vazias (ε). Isso é natural em parsers LL, mas o PLY usa LALR(1), que toleraria recursão à esquerda. Atender às duas restrições simultaneamente tornou a gramática significativamente mais verbosa.

**Decisão:** Para operadores aritméticos, a solução foi criar regras `add_tail` e `mul_tail` que retornam listas de `(operador, nó)`, processadas pela função auxiliar `_build_left()` para reconstruir a associatividade à esquerda na AST — mesmo com a gramática sendo recursiva à direita.

**Exemplo — regras geradas para adição:**
```
add_expr : mul_expr add_tail
         | mul_expr
add_tail : PLUS  mul_expr add_tail
         | PLUS  mul_expr
         | MINUS mul_expr add_tail
         | MINUS mul_expr
```

Sem a restrição, a regra seria apenas `add_expr : add_expr PLUS mul_expr | mul_expr`.

---

### 17.3 Conflitos no Parser LALR(1)

**Desafio:** O par `if` simples / `if-else` é a fonte clássica do conflito *dangling else* em parsers LALR(1). O PLY resolve por padrão favorecendo o `shift` (associando o `else` ao `if` mais interno), mas isso pode mascarar erros de gramática.

**Decisão:** As regras `p_if_simple` e `p_if_else` foram escritas como produções completamente separadas, deixando a gramática desambiguada sem depender do comportamento padrão do PLY.

**Limitação atual:** Não há suporte a `elif`. Adicionar essa construção exigiria uma nova produção na gramática e um novo nó na AST, o que introduziria conflitos S/R adicionais que precisariam ser resolvidos explicitamente.

---

### 17.4 Inferência de Tipos e Escopos Aninhados

**Desafio:** A linguagem é estaticamente tipada, mas a tipagem precisa ser inferida nas expressões em tempo de compilação. Operações como `+` têm comportamento diferente dependendo dos tipos dos operandos (`int + int`, `float + int`, `string + string`), e cada caso precisa ser tratado separadamente no `_type_of`.

**Decisão:** Implementar a tabela de símbolos com encadeamento de escopos (`SymbolTable.parent`), de forma que cada bloco aninhado (`if`, `while`, `for`) cria um novo escopo filho que herda os símbolos do pai. Promoção numérica `int → float` foi permitida implicitamente; demais conversões são erros.

**Limitação atual:** A condição dos blocos `ara` (if) e `jave` (while) exige o tipo `bool` estritamente. Expressões inteiras usadas como condição — padrão comum em C e Python — são rejeitadas pelo analisador semântico.

---

### 17.5 Emulação de Construções sem Equivalente em Python

**Desafio:** O `do-while` (`japo ... jave`) não existe em Python. A tradução direta não é possível.

**Decisão:** Emular com `while True:` seguido de um `if not (condição): break` ao final do bloco — o que preserva a semântica de execução garantida da primeira iteração.

**Python gerado para `japo ... jave`:**
```python
while True:
    # corpo do bloco
    if not (condição):
        break
```

**Limitação atual:** O `break` gerado encerra apenas o laço mais interno. Em blocos `do-while` aninhados, o comportamento é correto, mas a legibilidade do código gerado diminui.

---

### 17.6 Recuperação de Erros

**Desafio:** Em compiladores reais, é desejável que o processo continue após encontrar um erro, acumulando todos os problemas de uma vez para reportar ao usuário.

**Decisão:** O analisador semântico acumula erros em `self.errors` e continua a análise. O parser, por outro lado, interrompe ao primeiro erro sintático com `SyntaxError`, pois implementar recuperação de erros no PLY (via token especial `error`) aumentaria a complexidade da gramática consideravelmente.

**Limitação atual:** Um único erro de sintaxe encerra toda a compilação. O usuário não recebe informações sobre outros erros que possam existir no restante do código.

---

### Resumo das Limitações

| Limitação | Impacto | Complexidade para resolver |
|---|---|---|
| Sem `elif` | Encadeamento de condicionais verboso | Média |
| Condições de laço exigem `bool` estrito | Rejeita padrões comuns | Baixa |
| Recuperação de erros sintáticos ausente | Um erro por compilação | Alta |
| `IndentLexer` recria lexer por linha | Ineficiência em arquivos grandes | Baixa |
| Tabs equivalem fixamente a 4 espaços | Inconsistência com editores configurados diferente | Baixa |
| Sem funções ou procedimentos | Linguagem limitada a scripts lineares | Alta |

---

## 18. Conclusão

O **GuaCode** demonstra, de ponta a ponta, o funcionamento interno de uma linguagem de programação: o usuário escreve em Guarani, o sistema tokeniza o código, constrói uma árvore sintática, verifica tipos e escopos, gera Python equivalente e executa o resultado — tudo em uma única pipeline modular e testável.

Mais do que cumprir as etapas clássicas de um compilador, o projeto enfrentou decisões de design concretas que tornam sua implementação didaticamente relevante. A construção do `IndentLexer` mostrou na prática por que linguagens sensíveis à indentação exigem tratamento especial na análise léxica. A gramática sem recursão à esquerda e sem produções vazias evidenciou a diferença entre o que é formalmente correto e o que um gerador LALR(1) consegue processar eficientemente. A análise semântica com escopos aninhados e inferência de tipos ilustrou como um compilador pode detectar erros antes mesmo de o código ser executado.

A separação entre o núcleo (`guarani`), a interface de linha de comando (`main.py`) e a IDE gráfica (`ide.py`) — todos compartilhando o mesmo `GuaraniPipeline` — demonstra na prática como uma arquitetura modular permite reutilizar a mesma lógica de compilação em contextos diferentes, exatamente como ocorre em ferramentas reais como GCC, LLVM e o próprio CPython.

As limitações documentadas na seção anterior — ausência de `elif`, condições estritamente booleanas, recuperação de erros sintáticos e suporte a funções — não são falhas de execução, mas consequências naturais do escopo definido para a disciplina. Cada uma delas representa um ponto de extensão claro e tecnicamente viável para versões futuras da linguagem.

```
Escrever → Tokenizar → Analisar (sintaxe) → Verificar (semântica) → Gerar → Executar
```

O GuaCode é, em sua essência, uma prova de que os conceitos estudados em Teoria da Computação e Compiladores não são apenas formalismos teóricos — são os mesmos mecanismos que sustentam todas as linguagens de programação modernas.

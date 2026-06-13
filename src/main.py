"""
main.py — Ponto de Entrada do Transpilador Guarani
---------------------------------------------------
Fluxo: Código Guarani → Lexer → Parser → Análise Semântica → Transpilador → Python

Uso:
  python main.py teste.gua
  python main.py teste.gua -o saida.py
  python main.py teste.gua --run
  python main.py teste.gua --tokens
  python main.py teste.gua --ast
"""

import sys
import os
import argparse
import subprocess
from pathlib import Path

from guarani.lexer import IndentLexer
from guarani.parser import build_parser
from guarani.semantic import SemanticAnalyzer
from guarani.transpiler import Transpiler


def main():
    ap = argparse.ArgumentParser(
        description="Transpilador da linguagem Guarani para Python."
    )
    ap.add_argument("arquivo", help="arquivo fonte .gua")
    ap.add_argument("-o", "--output", default=None,
                    help="nome do arquivo Python gerado (padrão: output.py)")
    ap.add_argument("--run",    action="store_true", help="executar o código gerado")
    ap.add_argument("--tokens", action="store_true", help="exibir tokens (debug)")
    ap.add_argument("--ast",    action="store_true", help="exibir AST (debug)")
    args = ap.parse_args()

    if not os.path.isfile(args.arquivo):
        print(f"Arquivo não encontrado: {args.arquivo}")
        sys.exit(1)

    with open(args.arquivo, 'r', encoding='utf-8') as f:
        source = f.read()

    print(f"[ Guarani ] Compilando '{args.arquivo}' ...")

    # 1. Léxico
    try:
        lexer = IndentLexer(source)
    except IndentationError as e:
        print(f"[Erro de indentação] {e}")
        sys.exit(1)

    if args.tokens:
        print("\n--- Tokens ---")
        for tk in lexer.all_tokens():
            print(f"  {tk.type:12s} {tk.value!r}")
        try:
            lexer = IndentLexer(source)
        except IndentationError as e:
            print(f"[Erro de indentação] {e}")
            sys.exit(1)

    # 2. Sintático
    parser = build_parser()
    try:
        ast = parser.parse(lexer=lexer)
    except Exception as e:
        print(f"[Erro de análise sintática] {e}")
        sys.exit(1)
    if ast is None:
        print("Falha na análise sintática.")
        sys.exit(1)
    if args.ast:
        print("\n--- AST ---")
        print(ast)

    # 3. Semântico
    sa = SemanticAnalyzer()
    sa.analyze(ast)
    if sa.errors:
        print("\n--- Erros Semânticos ---")
        for err in sa.errors:
            print(err)
        sys.exit(1)

    # 4. Geração de código
    default_output = Path(__file__).resolve().parent.parent / 'generated' / 'output.py'
    out_path = args.output or str(default_output)
    output_dir = Path(out_path).resolve().parent
    output_dir.mkdir(parents=True, exist_ok=True)
    code = Transpiler(sa.global_scope).transpile(ast)
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(code)
    print(f"[ Guarani ] Código Python gerado em '{out_path}'.")

    # 5. Execução opcional
    if args.run:
        print(f"[ Guarani ] Executando '{out_path}'...\n" + "-" * 40)
        subprocess.run([sys.executable, out_path])


if __name__ == '__main__':
    main()

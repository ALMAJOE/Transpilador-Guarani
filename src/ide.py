import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from tkinter.scrolledtext import ScrolledText
from pathlib import Path

from guarani.pipeline import GuaraniPipeline


class LineNumbers(tk.Canvas):
    """Canvas widget that displays line numbers"""
    def __init__(self, parent, text_widget, **kwargs):
        super().__init__(parent, width=50, bg='#252526', highlightthickness=0, **kwargs)
        self.text_widget = text_widget
        text_widget.bind('<Configure>', self._update)
        text_widget.bind('<MouseWheel>', self._update)
        text_widget.bind('<Button-4>', self._update)
        text_widget.bind('<Button-5>', self._update)
        text_widget.bind('<KeyRelease>', self._update)

    def _update(self, *args):
        self.delete('all')
        i = self.text_widget.index('@0,0')
        while True:
            dline = self.text_widget.dlineinfo(i)
            if dline is None:
                break
            y = dline[1]
            linenum = str(i).split('.')[0]
            self.create_text(2, y, anchor='nw', text=linenum, fill='#858585', font=('Consolas', 10))
            i = self.text_widget.index(f'{i}+1line')


class CodeEditor(tk.Frame):
    """Text editor with line numbers"""
    def __init__(self, parent, **kwargs):
        super().__init__(parent, bg='#1e1e1e', **kwargs)
        
        # Frame for line numbers and text
        self.text_frame = tk.Frame(self, bg='#1e1e1e')
        self.text_frame.pack(fill=tk.BOTH, expand=True)
        
        # Text widget
        self.text = ScrolledText(
            self.text_frame,
            wrap='none',
            font=('Consolas', 11),
            bg='#1e1e1e',
            fg='#e0e0e0',
            insertbackground='#0098ff',
            selectbackground='#264f78',
            selectforeground='#e0e0e0',
            highlightthickness=0,
            padx=10,
            pady=5
        )
        self.text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Line numbers (created after text widget)
        self.line_numbers = LineNumbers(self.text_frame, self.text)
        self.line_numbers.pack(side=tk.LEFT, fill=tk.Y)

    def get(self, *args):
        return self.text.get(*args)

    def insert(self, *args):
        return self.text.insert(*args)

    def delete(self, *args):
        return self.text.delete(*args)


class GuaraniIDE(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('🐍 Guarani IDE - Transpilador Guarani')
        self.geometry('1200x800')
        self.minsize(900, 600)
        self.current_file = None
        self.pipeline = GuaraniPipeline()
        self.modified = False
        self._setup_styles()
        self._build_ui()
        self._bind_shortcuts()

    def _setup_styles(self):
        """Configure ttk styles for dark theme"""
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('TNotebook', background='#252526', borderwidth=0)
        style.configure('TNotebook.Tab', padding=[15, 8], font=('Segoe UI', 10), background='#3e3e42', foreground='#d4d4d4')
        style.map('TNotebook.Tab',
                  background=[('selected', '#0098ff')],
                  foreground=[('selected', '#ffffff')])
        style.configure('TFrame', background='#252526')

    def _bind_shortcuts(self):
        """Bind keyboard shortcuts"""
        self.bind('<Control-o>', lambda e: self.open_file())
        self.bind('<Control-s>', lambda e: self.save_file())
        self.bind('<Control-Shift-S>', lambda e: self.save_file_as())
        self.bind('<F5>', lambda e: self.run_output())
        self.bind('<Control-l>', lambda e: self.run_lexer())
        self.bind('<Control-p>', lambda e: self.run_parser())
        self.bind('<Control-m>', lambda e: self.run_semantic())
        self.bind('<Control-t>', lambda e: self.run_transpile())
        self.source_text.text.bind('<KeyRelease>', self._on_source_change)

    def _on_source_change(self, event=None):
        """Track if source code has been modified"""
        if not self.modified:
            self.modified = True
            self._update_title()

    def _update_title(self):
        """Update window title with file name and modified indicator"""
        if self.current_file:
            filename = Path(self.current_file).name
            prefix = '● ' if self.modified else ''
            self.title(f'🐍 Guarani IDE - {prefix}{filename}')
        else:
            prefix = '● ' if self.modified else ''
            self.title(f'🐍 Guarani IDE - {prefix}sem arquivo')

    def _build_ui(self):
        # Main container
        main_frame = ttk.Frame(self)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=0, pady=0)

        # Menu bar
        self._build_menu()

        # Toolbar section
        toolbar_frame = tk.Frame(self, bg='#252526', bd=1, relief=tk.RAISED)
        toolbar_frame.pack(fill=tk.X, padx=3, pady=3)
        self._build_toolbar(toolbar_frame)

        # Main workspace
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=3, pady=(0, 3))

        # Create tabs
        self.source_text = self._create_editor_tab('📝 Código Fonte (.gua)')
        self.python_text = self._create_readonly_tab('🐍 Python Gerado')
        self.tokens_text = self._create_readonly_tab('🔤 Tokens')
        self.ast_text = self._create_readonly_tab('🌳 Árvore (AST)')
        self.log_text = self._create_readonly_tab('📋 Logs')

        # Status bar
        self.status_var = tk.StringVar(value='🟢 Pronto')
        self.file_var = tk.StringVar(value='Sem arquivo')
        status_frame = tk.Frame(self, bg='#252526', bd=1, relief=tk.SUNKEN)
        status_frame.pack(fill=tk.X, side=tk.BOTTOM)
        
        tk.Label(status_frame, textvariable=self.status_var, bg='#252526', fg='#e0e0e0', anchor=tk.W, relief=tk.SUNKEN, bd=0).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5, pady=2)
        tk.Label(status_frame, textvariable=self.file_var, bg='#252526', fg='#858585', anchor=tk.E, width=30).pack(side=tk.RIGHT, padx=5)

        self._load_default_example()

    def _build_menu(self):
        """Build menu bar"""
        menubar = tk.Menu(self, bg='#252526', fg='#e0e0e0', activebackground='#0098ff', activeforeground='#ffffff')
        self.config(menu=menubar)

        # File menu
        file_menu = tk.Menu(menubar, bg='#252526', fg='#e0e0e0', activebackground='#0098ff', activeforeground='#ffffff')
        menubar.add_cascade(label='📂 Arquivo', menu=file_menu)
        file_menu.add_command(label='Abrir... (Ctrl+O)', command=self.open_file)
        file_menu.add_command(label='Salvar (Ctrl+S)', command=self.save_file)
        file_menu.add_command(label='Salvar Como... (Ctrl+Shift+S)', command=self.save_file_as)
        file_menu.add_separator()
        file_menu.add_command(label='Sair', command=self.quit)

        # Tools menu
        tools_menu = tk.Menu(menubar, bg='#252526', fg='#e0e0e0', activebackground='#0098ff', activeforeground='#ffffff')
        menubar.add_cascade(label='⚙️ Ferramentas', menu=tools_menu)
        tools_menu.add_command(label='Lexar (Ctrl+L)', command=self.run_lexer)
        tools_menu.add_command(label='Parse (Ctrl+P)', command=self.run_parser)
        tools_menu.add_command(label='Semântica (Ctrl+M)', command=self.run_semantic)
        tools_menu.add_command(label='Transpilar (Ctrl+T)', command=self.run_transpile)
        tools_menu.add_separator()
        tools_menu.add_command(label='Executar (F5)', command=self.run_output)
        tools_menu.add_separator()
        tools_menu.add_command(label='Limpar Saídas', command=self._clear_outputs)

        # Help menu
        help_menu = tk.Menu(menubar, bg='#252526', fg='#e0e0e0', activebackground='#0098ff', activeforeground='#ffffff')
        menubar.add_cascade(label='❓ Ajuda', menu=help_menu)
        help_menu.add_command(label='Sobre', command=self._show_about)

    def _build_toolbar(self, parent):
        """Build toolbar with organized buttons"""
        # File operations
        self._add_toolbar_button(parent, '📂 Abrir', self.open_file, tooltip='Ctrl+O')
        self._add_toolbar_button(parent, '💾 Salvar', self.save_file, tooltip='Ctrl+S')
        self._add_toolbar_button(parent, '💾 Salvar Como', self.save_file_as, tooltip='Ctrl+Shift+S')
        self._add_separator(parent)

        # Compilation steps
        self._add_toolbar_button(parent, '🔤 Lexar', self.run_lexer, tooltip='Ctrl+L')
        self._add_toolbar_button(parent, '🌳 Parse', self.run_parser, tooltip='Ctrl+P')
        self._add_toolbar_button(parent, '✓ Semântica', self.run_semantic, tooltip='Ctrl+M')
        self._add_toolbar_button(parent, '🔄 Transpilar', self.run_transpile, tooltip='Ctrl+T')
        self._add_separator(parent)

        # Execution
        self._add_toolbar_button(parent, '▶️ Executar', self.run_output, bg='#4caf50', tooltip='F5')
        self._add_toolbar_button(parent, '💾 Salvar Python', self.save_python_file)
        self._add_separator(parent)

        # Other
        self._add_toolbar_button(parent, '🗑️ Limpar', self._clear_outputs, bg='#ff9800')
        self._add_toolbar_button(parent, '🔧 Novo', self._new_file, bg='#2196f3')

    def _add_toolbar_button(self, parent, label, command, bg=None, tooltip=None):
        """Add a button to toolbar with optional tooltip"""
        btn = tk.Button(
            parent,
            text=label,
            command=command,
            bg=bg or '#2d2d2d',
            fg='#e0e0e0',
            activebackground='#0098ff',
            activeforeground='#ffffff',
            font=('Segoe UI', 9),
            relief=tk.FLAT,
            bd=0,
            padx=8,
            pady=3,
            cursor='hand2'
        )
        btn.pack(side=tk.LEFT, padx=2, pady=2)
        if tooltip:
            self._create_tooltip(btn, tooltip)

    def _add_separator(self, parent):
        """Add a separator in toolbar"""
        tk.Frame(parent, width=2, bg='#3e3e42').pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)

    def _create_tooltip(self, widget, text):
        """Create a simple tooltip"""
        def on_enter(e):
            tooltip = tk.Toplevel()
            tooltip.wm_overrideredirect(True)
            tooltip.wm_geometry(f'+{e.x_root+10}+{e.y_root+10}')
            label = tk.Label(tooltip, text=text, background='#3e3e42', fg='#e0e0e0', relief=tk.SOLID, bd=1, font=('Segoe UI', 8))
            label.pack()
            widget.tooltip = tooltip

        def on_leave(e):
            if hasattr(widget, 'tooltip'):
                widget.tooltip.destroy()
                delattr(widget, 'tooltip')

        widget.bind('<Enter>', on_enter)
        widget.bind('<Leave>', on_leave)

    def _create_editor_tab(self, title):
        """Create an editor tab with line numbers"""
        frame = ttk.Frame(self.notebook)
        editor = CodeEditor(frame)
        editor.pack(fill=tk.BOTH, expand=True)
        self.notebook.add(frame, text=title)
        return editor

    def _create_readonly_tab(self, title):
        """Create a read-only output tab"""
        frame = ttk.Frame(self.notebook)
        text_widget = ScrolledText(
            frame,
            wrap='none',
            font=('Consolas', 10),
            bg='#1e1e1e',
            fg='#e0e0e0',
            insertbackground='#0098ff',
            highlightthickness=0,
            padx=8,
            pady=5
        )
        text_widget.pack(fill=tk.BOTH, expand=True)
        self.notebook.add(frame, text=title)
        return text_widget

    def _load_default_example(self):
        """Load default example code"""
        sample = (
            'papapy idade = 20\n'
            'kuatia altura = 1.75\n'
            'nheeng nome = "Jose"\n'
            'anhete ativo = mante\n\n'
            'hai "Ola, mundo!"\n'
            'hai nome\n'
            'hai idade\n'
            'hai altura\n'
        )
        self.source_text.insert('1.0', sample)
        self._write_log('✅ IDE pronta. Edite o código ou abra um arquivo.')
        self.modified = False
        self._update_title()

    def _get_source(self):
        """Get source code from editor"""
        return self.source_text.get('1.0', tk.END).rstrip() + '\n'

    def _clear_outputs(self):
        """Clear all output tabs"""
        for widget in (self.python_text, self.tokens_text, self.ast_text, self.log_text):
            widget.delete('1.0', tk.END)

    def _set_widget_text(self, widget, text):
        """Set text in a widget"""
        widget.delete('1.0', tk.END)
        widget.insert('1.0', text)

    def _write_log(self, message):
        """Write to log tab"""
        self.log_text.insert(tk.END, message + '\n')
        self.log_text.see(tk.END)

    def _set_status(self, message, duration=None):
        """Update status bar"""
        self.status_var.set(message)
        self.update_idletasks()

    def _show_about(self):
        """Show about dialog"""
        messagebox.showinfo('Sobre', 'Guarani IDE v1.0\n\nTranspilador de Guarani para Python\n\nUsando PLY (Python Lex-Yacc)')

    def _new_file(self):
        """Create a new file"""
        if self.modified:
            if not messagebox.askyesno('Novo Arquivo', 'Você tem alterações não salvas. Descartar?'):
                return
        self.source_text.delete('1.0', tk.END)
        self._clear_outputs()
        self.current_file = None
        self.modified = False
        self._update_title()
        self.file_var.set('Novo arquivo')
        self._write_log('📄 Novo arquivo criado')

    def open_file(self):
        """Open a file"""
        if self.modified:
            if not messagebox.askyesno('Abrir Arquivo', 'Você tem alterações não salvas. Descartar?'):
                return
        path = filedialog.askopenfilename(
            filetypes=[('Guarani files', '*.gua'), ('Text files', '*.txt'), ('All files', '*.*')]
        )
        if not path:
            return
        try:
            with open(path, 'r', encoding='utf-8') as file:
                content = file.read()
            self.current_file = path
            self.source_text.delete('1.0', tk.END)
            self.source_text.insert('1.0', content)
            self._clear_outputs()
            self.modified = False
            self._update_title()
            filename = Path(path).name
            self.file_var.set(filename)
            self._write_log(f'✅ Aberto: {filename}')
            self._set_status(f'🟢 {filename}')
        except Exception as exc:
            self._write_log(f'❌ Erro: {exc}')
            messagebox.showerror('Erro', f'Não foi possível abrir:\n{exc}')

    def save_file(self):
        """Save current file"""
        if self.current_file is None:
            return self.save_file_as()
        self._save_to_path(self.current_file)

    def save_file_as(self):
        """Save file with new name"""
        path = filedialog.asksaveasfilename(
            defaultextension='.gua',
            filetypes=[('Guarani files', '*.gua'), ('Text files', '*.txt'), ('All files', '*.*')]
        )
        if not path:
            return
        self.current_file = path
        self._save_to_path(path)

    def _save_to_path(self, path):
        """Save content to path"""
        try:
            content = self.source_text.get('1.0', tk.END)
            with open(path, 'w', encoding='utf-8') as file:
                file.write(content)
            filename = Path(path).name
            self.file_var.set(filename)
            self.modified = False
            self._update_title()
            self._write_log(f'✅ Salvo: {filename}')
            self._set_status(f'🟢 Salvo')
        except Exception as exc:
            self._write_log(f'❌ Erro: {exc}')
            messagebox.showerror('Erro', f'Não foi possível salvar:\n{exc}')

    def save_python_file(self):
        """Save transpiled Python code"""
        code = self.python_text.get('1.0', tk.END).strip()
        if not code:
            messagebox.showwarning('Aviso', 'Não há código Python gerado. Execute a transpilação primeiro.')
            return
        path = filedialog.asksaveasfilename(
            defaultextension='.py',
            filetypes=[('Python files', '*.py'), ('All files', '*.*')]
        )
        if not path:
            return
        try:
            with open(path, 'w', encoding='utf-8') as file:
                file.write(code)
            filename = Path(path).name
            self._write_log(f'✅ Python salvo: {filename}')
        except Exception as exc:
            messagebox.showerror('Erro', f'Erro ao salvar:\n{exc}')

    def run_lexer(self):
        """Run lexer"""
        self.log_text.delete('1.0', tk.END)
        try:
            self._set_status('⚙️ Analisando léxica...')
            source = self._get_source()
            tokens = self.pipeline.lex(source)
            output = '\n'.join(f'{t.type:12s} {t.value!r}' for t in tokens)
            self._set_widget_text(self.tokens_text, output)
            self._write_log(f'✅ Análise léxica concluída\n📊 Total: {len(tokens)} tokens')
            self._set_status(f'🟢 {len(tokens)} tokens')
            self.notebook.select(2)
        except Exception as exc:
            self._write_log(f'❌ Erro léxico: {exc}')
            self._set_status('🔴 Erro')
            messagebox.showerror('Erro Léxico', str(exc))

    def run_parser(self):
        """Run parser"""
        self.log_text.delete('1.0', tk.END)
        try:
            self._set_status('⚙️ Analisando sintaxe...')
            source = self._get_source()
            ast = self.pipeline.parse(source)
            self._set_widget_text(self.ast_text, repr(ast))
            self._write_log('✅ Análise sintática concluída')
            self._set_status('🟢 Parser OK')
            self.notebook.select(3)
        except Exception as exc:
            self._write_log(f'❌ Erro sintático: {exc}')
            self._set_status('🔴 Erro')
            messagebox.showerror('Erro Sintático', str(exc))

    def run_semantic(self):
        """Run semantic analysis"""
        self.log_text.delete('1.0', tk.END)
        try:
            self._set_status('⚙️ Analisando semântica...')
            source = self._get_source()
            ast = self.pipeline.parse(source)
            analyzer = self.pipeline.analyze(ast)
            self._set_widget_text(self.ast_text, repr(ast))
            if analyzer.errors:
                self._write_log('❌ Erros semânticos encontrados:\n')
                for err in analyzer.errors:
                    self._write_log(f'  ⚠️ {err}')
                self._set_status(f'🔴 {len(analyzer.errors)} erro(s)')
                messagebox.showwarning('Erros Semânticos', f'{len(analyzer.errors)} erro(s) encontrado(s)')
            else:
                self._write_log('✅ Análise semântica concluída com sucesso')
                self._set_status('🟢 Semântica OK')
            self.notebook.select(4)
        except Exception as exc:
            self._write_log(f'❌ Erro: {exc}')
            self._set_status('🔴 Erro')
            messagebox.showerror('Erro', str(exc))

    def run_transpile(self):
        """Run transpiler"""
        self.log_text.delete('1.0', tk.END)
        try:
            self._set_status('⚙️ Transpilando...')
            source = self._get_source()
            ast = self.pipeline.parse(source)
            analyzer = self.pipeline.analyze(ast)
            if analyzer.errors:
                self._write_log('❌ Não é possível transpilar com erros semânticos:\n')
                for err in analyzer.errors:
                    self._write_log(f'  ⚠️ {err}')
                self._set_status('🔴 Transpilação bloqueada')
                messagebox.showwarning('Erros', 'Corrija os erros semânticos antes.')
                self.notebook.select(4)
                return
            code = self.pipeline.transpile(ast, analyzer.global_scope)
            self._set_widget_text(self.python_text, code)
            lines = len(code.split('\n'))
            self._write_log(f'✅ Transpilação concluída\n📝 Python gerado: {lines} linhas')
            self._set_status(f'🟢 {lines} linhas')
            self.notebook.select(1)
        except Exception as exc:
            self._write_log(f'❌ Erro: {exc}')
            self._set_status('🔴 Erro')
            messagebox.showerror('Erro', str(exc))

    def run_output(self):
        """Run full pipeline and execute"""
        self.log_text.delete('1.0', tk.END)
        try:
            self._set_status('⚙️ Executando...')
            source = self._get_source()
            ast = self.pipeline.parse(source)
            analyzer = self.pipeline.analyze(ast)
            if analyzer.errors:
                self._write_log('❌ Não é possível executar com erros semânticos:\n')
                for err in analyzer.errors:
                    self._write_log(f'  ⚠️ {err}')
                self._set_status('🔴 Execução bloqueada')
                self.notebook.select(4)
                return
            code = self.pipeline.transpile(ast, analyzer.global_scope)
            self._set_widget_text(self.python_text, code)
            stdout, stderr = self.pipeline.execute(code)
            
            self._write_log('━' * 50)
            if stderr:
                self._write_log(f'❌ Erro na execução:\n{stderr}')
                self._set_status('🔴 Erro')
            else:
                output = stdout.strip() if stdout.strip() else '(vazio)'
                self._write_log(f'✅ Executado com sucesso\n\n📤 Saída:\n{output}')
                self._set_status('🟢 Executado')
            self.notebook.select(4)
        except Exception as exc:
            self._write_log(f'❌ Erro: {exc}')
            self._set_status('🔴 Erro')
            messagebox.showerror('Erro', str(exc))


if __name__ == '__main__':
    app = GuaraniIDE()
    app.mainloop()

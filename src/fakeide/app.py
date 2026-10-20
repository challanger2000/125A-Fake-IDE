"""Tkinter desktop UI for a fully simulated development environment."""
from __future__ import annotations

import re
import sys
import tkinter as tk
from tkinter import ttk

from .simulation import FILES, HEADERS, Event, SimEngine

BG = '#0c111b'
PANEL = '#111827'
EDITOR = '#0f1624'
SIDEBAR = '#121c2a'
BORDER = '#293548'
TEXT = '#d6e1ef'
MUTED = '#8093a9'
BLUE = '#69b5ff'
GREEN = '#5fd59c'
YELLOW = '#e8bd6c'
RED = '#f77987'
PURPLE = '#c6a0f6'
FONT = ('Consolas', 12)


class FakeIDEApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.engine = SimEngine()
        self.playing = True
        self.elapsed = 0
        self.type_queue = ''
        self.mode = tk.StringVar(value='Normal')
        self.speed = tk.StringVar(value='1×')
        self.project_file = FILES[0]
        self.show_warning = False
        self.root.title('125A Fake IDE | Runtime Workspace — SIMULATION')
        self.root.configure(bg=BG)
        self.root.minsize(1100, 650)
        self.root.geometry('1530x900')
        try:
            self.root.state('zoomed')
        except tk.TclError:
            pass
        self._init_style()
        self._layout()
        self._bind_keys()
        self._load_file(self.project_file)
        self._write_terminal('125A Fake IDE v0.1.0  |  SIMULATION MODE', 'info')
        self._write_terminal('All output is staged. No compiler, files or network are accessed.', 'info')
        self._write_terminal('Workspace loaded: Runtime / Release x64', 'log')
        self._animate()

    def _init_style(self) -> None:
        style = ttk.Style(self.root)
        style.theme_use('clam')
        style.configure('Dark.Treeview', background=SIDEBAR, fieldbackground=SIDEBAR,
                        foreground=TEXT, borderwidth=0, rowheight=29,
                        font=('Segoe UI', 11))
        style.map('Dark.Treeview', background=[('selected', '#243a52')],
                  foreground=[('selected', '#e8f5ff')])
        style.configure('Dark.Treeview.Heading', background=PANEL, foreground=TEXT)
        style.configure('Dark.TCombobox', foreground=TEXT, background=PANEL,
                        fieldbackground=PANEL, arrowcolor=TEXT, padding=4)
        style.map('Dark.TCombobox', fieldbackground=[('readonly', PANEL)],
                  foreground=[('readonly', TEXT)], selectbackground=[('readonly', PANEL)],
                  selectforeground=[('readonly', TEXT)])
        style.configure('Build.Horizontal.TProgressbar', troughcolor=BG,
                        background=BLUE, borderwidth=0, thickness=5)

    def _label(self, parent: tk.Misc, text: str, *, fg: str = TEXT,
               bg: str = PANEL, font: tuple | None = None, **kwargs) -> tk.Label:
        return tk.Label(parent, text=text, bg=bg, fg=fg, anchor='w',
                        font=font or ('Segoe UI', 10), **kwargs)

    def _button(self, parent: tk.Misc, title: str, fn, *, accent: bool = False) -> tk.Button:
        return tk.Button(parent, text=title, command=fn, bg='#1b3550' if accent else '#1b2637',
                         fg='#e5f2ff', activebackground='#254662', activeforeground='white',
                         relief='flat', bd=0, padx=13, pady=7, cursor='hand2',
                         font=('Segoe UI', 10, 'bold' if accent else 'normal'))

    def _layout(self) -> None:
        header = tk.Frame(self.root, bg=BG, height=64)
        header.pack(fill='x', padx=17)
        header.pack_propagate(False)
        tl = tk.Frame(header, bg=BG)
        tl.pack(side='left', fill='y')
        self._label(tl, '125A  /  RUNTIME WORKSPACE', bg=BG,
                    font=('Segoe UI Semibold', 17, 'bold')).pack(side='top', anchor='w', pady=(10, 0))
        self._label(tl, 'Developer Edition    •    Windows x64    •    C++23',
                    bg=BG, fg=MUTED, font=('Segoe UI', 10)).pack(anchor='w')
        self._label(header, '●  SIMULATION MODE   |   NO REAL BUILD',
                    bg=BG, fg=YELLOW, font=('Segoe UI', 11, 'bold')).pack(side='right', padx=9)

        toolbar = tk.Frame(self.root, bg=PANEL, height=56, highlightbackground=BORDER,
                           highlightthickness=1)
        toolbar.pack(fill='x', padx=14, pady=(1, 9))
        toolbar.pack_propagate(False)
        controls = tk.Frame(toolbar, bg=PANEL)
        controls.pack(side='left', pady=8, padx=10)
        self.play_button = self._button(controls, '❚❚ Pause (F5)', self._toggle, accent=True)
        self.play_button.pack(side='left', padx=(0, 6))
        self._button(controls, '▶ Build (F7)', self._start_build).pack(side='left', padx=(0, 6))
        self._button(controls, '⚠ Warnung (F6)', self._warning).pack(side='left', padx=(0, 6))
        self._button(controls, '✖ Fehler-Build', lambda: self._start_build(True)).pack(side='left', padx=(0, 6))
        self._button(controls, '↻ Reset', self._reset).pack(side='left', padx=(0, 6))
        self.fullscreen_button = self._button(controls, '⛶ Vollbild (F11)', self._fullscreen)
        self.fullscreen_button.pack(side='left')
        selectors = tk.Frame(toolbar, bg=PANEL)
        selectors.pack(side='right', padx=13, pady=9)
        self._label(selectors, 'MODUS', bg=PANEL, fg=MUTED).pack(side='left', padx=(0, 6))
        ttk.Combobox(selectors, textvariable=self.mode, values=['Normal', 'Intensiv'],
                     width=10, state='readonly', style='Dark.TCombobox').pack(side='left', padx=(0, 12))
        self._label(selectors, 'TEMPO', bg=PANEL, fg=MUTED).pack(side='left', padx=(0, 6))
        ttk.Combobox(selectors, textvariable=self.speed, values=['0.5×', '1×', '2×', '4×'],
                     width=6, state='readonly', style='Dark.TCombobox').pack(side='left')

        main = tk.PanedWindow(self.root, orient='horizontal', bg=BORDER, sashwidth=5,
                              showhandle=False, relief='flat', bd=0)
        main.pack(fill='both', expand=True, padx=14)
        self.explorer = tk.Frame(main, bg=SIDEBAR, width=255)
        self.workspace = tk.Frame(main, bg=EDITOR)
        self.inspector = tk.Frame(main, bg=SIDEBAR, width=330)
        main.add(self.explorer, minsize=180, width=255, stretch='never')
        main.add(self.workspace, minsize=480, stretch='always')
        main.add(self.inspector, minsize=240, width=330, stretch='never')
        self._make_explorer()
        self._make_workspace()
        self._make_inspector()

        status = tk.Frame(self.root, bg='#122b43', height=33)
        status.pack(fill='x', pady=(9, 0))
        status.pack_propagate(False)
        self.status_left = self._label(status, '  ◉  Ready    |    Runtime x64    |    SIMULATED',
                                       bg='#122b43', fg='#b8dcff', font=('Segoe UI', 10))
        self.status_left.pack(side='left', pady=7)
        self.status_right = self._label(status, 'Ln 1, Col 1   |   UTF-8   |   C++   |   1920×1080',
                                        bg='#122b43', fg='#b8dcff', font=('Segoe UI', 10))
        self.status_right.pack(side='right', padx=18, pady=7)

    def _make_explorer(self) -> None:
        self._label(self.explorer, ' EXPLORER', bg=SIDEBAR, fg=MUTED,
                    font=('Segoe UI Semibold', 10, 'bold')).pack(fill='x', pady=(14, 10), padx=10)
        self.tree = ttk.Treeview(self.explorer, show='tree', style='Dark.Treeview', selectmode='browse')
        self.tree.pack(fill='both', expand=True, padx=(7, 2), pady=(0, 5))
        r = self.tree.insert('', 'end', text='▾  125A RUNTIME', open=True)
        nodes: dict[str, str] = {'': r}
        self._tree_ids: dict[str, str] = {}
        for file in FILES:
            directory, basename = file.rsplit('/', 1)
            p = ''
            for seg in directory.split('/'):
                new_p = f'{p}/{seg}'.strip('/')
                if new_p not in nodes:
                    nodes[new_p] = self.tree.insert(nodes[p], 'end', text='▸  ' + seg, open=True)
                p = new_p
            self._tree_ids[file] = self.tree.insert(nodes[p], 'end', text='  ' + basename)
        for file in ['CMakeLists.txt', 'README.md']:
            self.tree.insert(r, 'end', text='  ' + file)
        self.tree.bind('<<TreeviewSelect>>', self._on_file_selected)
        self.tree.selection_set(self._tree_ids[FILES[0]])
        self._label(self.explorer, '  OUTLINE  •  SYMBOLS', bg=SIDEBAR, fg=MUTED,
                    font=('Segoe UI Semibold', 10, 'bold')).pack(fill='x', pady=(11, 7))
        outline = tk.Frame(self.explorer, bg=SIDEBAR)
        outline.pack(fill='x', padx=15, pady=(0, 20))
        for name in ['ƒ  RuntimeEngine::update()', 'ƒ  initialize() noexcept',
                     '◇  Config', 'ƒ  updateWorkers()']:
            self._label(outline, name, bg=SIDEBAR, fg='#b1c5dc',
                        font=('Consolas', 10)).pack(fill='x', pady=4)

    def _make_workspace(self) -> None:
        center = tk.PanedWindow(self.workspace, orient='vertical', bg=BORDER, sashwidth=6,
                                relief='flat', bd=0)
        center.pack(fill='both', expand=True)
        editor_panel = tk.Frame(center, bg=EDITOR)
        console_panel = tk.Frame(center, bg=EDITOR)
        center.add(editor_panel, minsize=250, stretch='always')
        center.add(console_panel, minsize=130, height=260, stretch='never')
        tabs = tk.Frame(editor_panel, bg=PANEL, height=38)
        tabs.pack(fill='x')
        tabs.pack_propagate(False)
        self.tab_label = self._label(tabs, '  ◉  runtime_engine.cpp  ×  ', bg='#202f45',
                                      fg='#cde8ff', font=('Segoe UI', 11, 'bold'))
        self.tab_label.pack(side='left', fill='y', padx=(8, 0))
        self._label(tabs, '   config.hpp   ×  ', bg=PANEL, fg=MUTED,
                    font=('Segoe UI', 10)).pack(side='left', fill='y')
        self._label(tabs, '●   LIVE EDITOR', bg=PANEL, fg=GREEN,
                    font=('Segoe UI', 9, 'bold')).pack(side='right', padx=12)
        pathbar = tk.Frame(editor_panel, bg=EDITOR, height=28)
        pathbar.pack(fill='x')
        self.path_label = self._label(pathbar, self.project_file, bg=EDITOR, fg=MUTED,
                                      font=('Segoe UI', 9))
        self.path_label.pack(side='left', padx=17, pady=5)
        codearea = tk.Frame(editor_panel, bg=EDITOR)
        codearea.pack(fill='both', expand=True)
        self.lines = tk.Text(codearea, width=5, wrap='none', bg=EDITOR, fg='#657791',
                             font=FONT, borderwidth=0, padx=8, pady=8, state='disabled',
                             takefocus=0, cursor='arrow', highlightthickness=0)
        self.lines.pack(side='left', fill='y')
        scrollbar = tk.Scrollbar(codearea, orient='vertical', bg=PANEL, troughcolor=PANEL)
        scrollbar.pack(side='right', fill='y')
        self.code = tk.Text(codearea, bg=EDITOR, fg=TEXT, insertbackground=BLUE,
                            font=FONT, borderwidth=0, wrap='none', padx=10, pady=8,
                            highlightthickness=0, spacing1=1, spacing3=2,
                            yscrollcommand=lambda a, b: (scrollbar.set(a, b), self.lines.yview_moveto(a)))
        self.code.pack(fill='both', expand=True)
        scrollbar.configure(command=lambda *a: (self.code.yview(*a), self.lines.yview(*a)))
        # Suppress editing without swallowing global hotkeys such as F11.
        self.code.bind('<Key>', self._on_code_key)
        self.code.tag_configure('keyword', foreground=PURPLE)
        self.code.tag_configure('string', foreground=GREEN)
        self.code.tag_configure('number', foreground=YELLOW)
        self.code.tag_configure('comment', foreground='#6f8fa0')
        self.code.tag_configure('type', foreground=BLUE)
        self.code.tag_configure('active', background='#1a2739')

        ctop = tk.Frame(console_panel, bg=PANEL, height=37)
        ctop.pack(fill='x')
        ctop.pack_propagate(False)
        self._label(ctop, '  TERMINAL   /   OUTPUT', bg=PANEL,
                    font=('Segoe UI Semibold', 10, 'bold')).pack(side='left', fill='y')
        self._label(ctop, 'powershell  •  simulation', bg=PANEL, fg=MUTED,
                    font=('Segoe UI', 9)).pack(side='right', padx=11, fill='y')
        termarea = tk.Frame(console_panel, bg='#0b111b')
        termarea.pack(fill='both', expand=True)
        self.terminal = tk.Text(termarea, bg='#0b111b', fg='#abbcd0', font=('Consolas', 10),
                                padx=12, pady=9, wrap='word', borderwidth=0,
                                highlightthickness=0, state='disabled')
        self.terminal.pack(fill='both', expand=True)
        for name, color in [('info', BLUE), ('warn', YELLOW), ('error', RED),
                            ('build', GREEN), ('tests', GREEN), ('log', '#a8b9cb')]:
            self.terminal.tag_configure(name, foreground=color)
        self.progress = ttk.Progressbar(console_panel, mode='indeterminate',
                                         style='Build.Horizontal.TProgressbar', length=200)
        self.progress.pack(fill='x')

    def _make_inspector(self) -> None:
        self._label(self.inspector, '  DIAGNOSTICS', bg=SIDEBAR, fg=MUTED,
                    font=('Segoe UI Semibold', 10, 'bold')).pack(fill='x', pady=(14, 10))
        cards = tk.Frame(self.inspector, bg=SIDEBAR)
        cards.pack(fill='x', padx=10, pady=(0, 14))
        for i, (title, attr, color) in enumerate([('WARNINGS', 'warn_value', YELLOW),
                                                  ('ERRORS', 'error_value', RED),
                                                  ('TEST RUNS', 'test_value', GREEN)]):
            block = tk.Frame(cards, bg=PANEL, padx=10, pady=9)
            block.grid(row=0, column=i, sticky='ew', padx=3)
            cards.columnconfigure(i, weight=1)
            self._label(block, title, bg=PANEL, fg=MUTED,
                        font=('Segoe UI', 8)).pack(anchor='w')
            value = self._label(block, '00', bg=PANEL, fg=color,
                                font=('Consolas', 18, 'bold'))
            value.pack(anchor='w')
            setattr(self, attr, value)
        self._label(self.inspector, 'LIVE PROBLEMS / ANALYSIS', bg=SIDEBAR, fg=TEXT,
                    font=('Segoe UI Semibold', 10, 'bold')).pack(anchor='w', padx=14, pady=(0, 7))
        self.diagnostics = tk.Text(self.inspector, bg=SIDEBAR, fg=TEXT,
                                   padx=13, pady=7, height=14, wrap='word', borderwidth=0,
                                   highlightthickness=0, font=('Consolas', 10), state='disabled')
        self.diagnostics.pack(fill='both', expand=True)
        self.diagnostics.tag_configure('warn', foreground=YELLOW, spacing3=12)
        self.diagnostics.tag_configure('error', foreground=RED, spacing3=12)
        self.diagnostics.tag_configure('info', foreground='#9eb6cd', spacing3=9)
        self._add_diagnostic('info', 'Analyzer idle. Waiting for code changes.')

        monitor = tk.Frame(self.inspector, bg=PANEL)
        monitor.pack(fill='x', padx=10, pady=(13, 10))
        self._label(monitor, '  RUNTIME MONITOR  (simuliert)', bg=PANEL, fg=MUTED,
                    font=('Segoe UI', 9, 'bold')).pack(fill='x', pady=(10, 5))
        self.cpu_label = self._label(monitor, 'CPU: 00%          Threads: 16', bg=PANEL,
                                     font=('Consolas', 10))
        self.cpu_label.pack(padx=13, pady=(5, 4), fill='x')
        self.cpu_bar = tk.Canvas(monitor, bg='#223248', height=8, highlightthickness=0)
        self.cpu_bar.pack(fill='x', padx=13)
        self.ram_label = self._label(monitor, 'RAM:  5.1 GB      Cache: nominal',
                                     bg=PANEL, font=('Consolas', 10))
        self.ram_label.pack(padx=13, pady=(12, 13), fill='x')

    def _on_file_selected(self, _event=None) -> None:
        selected = self.tree.selection()
        if not selected:
            return
        for file, item in self._tree_ids.items():
            if selected[0] == item and file != self.project_file:
                self._load_file(file)
                return

    def _load_file(self, file: str) -> None:
        self.project_file = file
        self.type_queue = ''
        self.code.delete('1.0', 'end')
        self.code.insert('1.0', HEADERS[file] + '\n')
        self.path_label.config(text='workspace  >  ' + file.replace('/', '  >  '))
        self.tab_label.config(text=f'  ◉  {file.rsplit("/", 1)[-1]}  ×  ')
        if self.tree.selection() != (self._tree_ids[file],):
            self.tree.selection_set(self._tree_ids[file])
        self._highlight()
        self._sync_lines()

    def _highlight(self) -> None:
        # Only a few hundred lines at most; each update is bounded.
        source = self.code.get('1.0', 'end-1c')
        for tag in ('keyword', 'string', 'number', 'comment', 'type'):
            self.code.tag_remove(tag, '1.0', 'end')
        patterns = [
            ('keyword', r'\b(?:namespace|class|struct|public|private|if|return|constexpr|const|explicit|auto|bool|void|using|static|noexcept|include|pragma)\b'),
            ('type', r'\b(?:uint32_t|uint64_t|size_t|float|Config|RuntimeEngine|Task|TaskContext|RenderState|Diagnostic|std)\b'),
            ('number', r'\b\d+(?:\.\d+)?f?\b'),
            ('string', r'"[^"\n]*"'),
            ('comment', r'//[^\n]*'),
        ]
        for tag, pattern in patterns:
            for match in re.finditer(pattern, source):
                self.code.tag_add(tag, f'1.0+{match.start()}c', f'1.0+{match.end()}c')
        self.code.tag_remove('active', '1.0', 'end')
        self.code.tag_add('active', 'end-2l linestart', 'end-2l lineend')

    def _sync_lines(self) -> None:
        count = max(1, int(self.code.index('end-1c').split('.')[0]))
        self.lines.configure(state='normal')
        self.lines.delete('1.0', 'end')
        self.lines.insert('1.0', '\n'.join(str(i) for i in range(1, count + 1)))
        self.lines.configure(state='disabled')
        self.lines.yview_moveto(self.code.yview()[0])
        line, col = self.code.index('end-1c').split('.')
        self.status_right.config(text=f'Ln {line}, Col {col}   |   UTF-8   |   C++23   |   x64  ')

    def _write_terminal(self, message: str, kind: str = 'log') -> None:
        self.terminal.configure(state='normal')
        self.terminal.insert('end', '[SIM] ' + message + '\n', kind)
        if int(self.terminal.index('end-1c').split('.')[0]) > 350:
            self.terminal.delete('1.0', '65.0')
        self.terminal.see('end')
        self.terminal.configure(state='disabled')

    def _add_diagnostic(self, kind: str, message: str) -> None:
        self.diagnostics.configure(state='normal')
        self.diagnostics.insert('1.0', ('⚠  ' if kind == 'warn' else '✖  ' if kind == 'error' else '●  ') + message + '\n\n', kind)
        if int(self.diagnostics.index('end-1c').split('.')[0]) > 90:
            self.diagnostics.delete('75.0', 'end')
        self.diagnostics.configure(state='disabled')

    def _apply_event(self, event: Event) -> None:
        if event.kind == 'file':
            self._load_file(event.file)
            self._add_diagnostic('info', f'Indexed {event.file}')
        elif event.kind == 'code':
            if self.project_file == event.file:
                self.type_queue += event.message + '\n'
        else:
            self._write_terminal(event.message, event.kind)
            if event.kind in ('warn', 'error'):
                location = f'{event.file}:{event.line}' if event.file else 'linker'
                self._add_diagnostic(event.kind, location + '\n' + event.message)
            elif event.kind in ('build', 'tests'):
                self._add_diagnostic('info', event.message)

    def _start_build(self, fail: bool = False) -> None:
        self._apply_event(self.engine.start_build(fail=fail))
        self.progress.start(17)
        if not self.playing:
            self._toggle()

    def _warning(self) -> None:
        self._apply_event(self.engine.inject_warning())
        self._update_status()

    def _toggle(self) -> None:
        self.playing = not self.playing
        self.play_button.config(text='❚❚ Pause (F5)' if self.playing else '▶ Start (F5)')
        self._update_status()

    def _reset(self) -> None:
        self.engine.reset()
        self.type_queue = ''
        self.elapsed = 0
        self._load_file(FILES[0])
        self.terminal.configure(state='normal')
        self.terminal.delete('1.0', 'end')
        self.terminal.configure(state='disabled')
        self.diagnostics.configure(state='normal')
        self.diagnostics.delete('1.0', 'end')
        self.diagnostics.configure(state='disabled')
        self.progress.stop()
        self._add_diagnostic('info', 'Simulation reset. Ready.')
        self._write_terminal('Workspace reinitialized. SIMULATION MODE', 'info')
        self._update_status()

    def _update_status(self) -> None:
        self.warn_value.config(text=f'{self.engine.warning_count:02d}')
        self.error_value.config(text=f'{self.engine.error_count:02d}')
        self.test_value.config(text=f'{self.engine.test_count:02d}')
        state = 'PAUSED' if not self.playing else self.engine.phase
        self.status_left.config(text=f'  ◉  {state}   |   Builds: {self.engine.build_count}   |   SIMULATION / OFFLINE')
        cpu = self.engine.cpu()
        self.cpu_label.config(text=f'CPU: {cpu:02d}%          Threads: 16')
        self.ram_label.config(text=f'RAM:  {self.engine.ram()}      Cache: nominal')
        self.cpu_bar.delete('all')
        self.cpu_bar.update_idletasks()
        width = self.cpu_bar.winfo_width()
        if width > 0:
            self.cpu_bar.create_rectangle(0, 0, width * cpu / 100, 8, fill=BLUE, outline='')

    def _animate(self) -> None:
        if self.playing:
            loops = {'0.5×': 1, '1×': 1, '2×': 2, '4×': 4}.get(self.speed.get(), 1)
            for _ in range(loops):
                for event in self.engine.step():
                    self._apply_event(event)
                if self.mode.get() == 'Intensiv' and self.engine.tick_count % 61 == 0:
                    self._apply_event(self.engine.inject_warning())
                if self.type_queue:
                    chars = 2 if self.speed.get() == '0.5×' else 4
                    chunk, self.type_queue = self.type_queue[:chars], self.type_queue[chars:]
                    self.code.insert('end-1c', chunk)
                    if '\n' in chunk or self.engine.tick_count % 4 == 0:
                        self._highlight()
                        self._sync_lines()
                    self.code.see('end')
                if self.engine.phase != 'BUILDING':
                    self.progress.stop()
                if int(self.code.index('end-1c').split('.')[0]) > 240:
                    self.code.delete('17.0', '55.0')
            self.elapsed += 1
        if self.elapsed % 8 == 0:
            self._update_status()
        self.root.after(75 if self.speed.get() != '0.5×' else 140, self._animate)

    def _bind_keys(self) -> None:
        for sequence in ('<F5>', '<F6>', '<F7>', '<F11>', '<Escape>', '<Control-r>'):
            self.root.bind(sequence, self._handle_shortcut)

    def _handle_shortcut(self, event) -> str | None:
        key = event.keysym
        if key == 'F5':
            self._toggle()
        elif key == 'F6':
            self._warning()
        elif key == 'F7':
            self._start_build()
        elif key == 'F11':
            self._fullscreen()
        elif key == 'Escape':
            self._exit_fullscreen()
        elif key.lower() == 'r' and (event.state & 0x4):
            self._reset()
        else:
            return None
        return 'break'

    def _on_code_key(self, event) -> str:
        # The fake editor never accepts user text, but must keep hotkeys working.
        self._handle_shortcut(event)
        return 'break'

    def _set_fullscreen(self, enabled: bool) -> None:
        # Fullscreen hides the Windows title bar and taskbar, unlike 'zoomed'.
        self.root.attributes('-fullscreen', enabled)
        self.fullscreen_button.config(
            text='▣ Fenster (F11)' if enabled else '⛶ Vollbild (F11)'
        )

    def _fullscreen(self, _event=None) -> None:
        self._set_fullscreen(not bool(self.root.attributes('-fullscreen')))

    def _exit_fullscreen(self) -> None:
        if bool(self.root.attributes('-fullscreen')):
            self._set_fullscreen(False)


def self_test() -> int:
    """Safe headless smoke check suitable for Windows CI after packaging."""
    engine = SimEngine()
    engine.start_build()
    for _ in range(35):
        engine.step()
        if engine.phase == 'EDITING':
            break
    return 0 if engine.last_build_ok is True and engine.test_count == 1 else 1


def main() -> None:
    if '--self-test' in sys.argv:
        sys.exit(self_test())
    root = tk.Tk()
    FakeIDEApp(root)
    root.mainloop()

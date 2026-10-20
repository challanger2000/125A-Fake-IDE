# 125A Fake IDE — Static Product Design v0.1.0

## Product scope
A standalone Windows **simulation**, not a compiler, IDE, debugger, emulator, network utility or source-code editor. The application must not run a shell, read private user projects, transmit data, persist synthetic source, or modify the developer's PC. All code, build progress, memory and CPU readouts, warnings, tests and errors are fictitious, and the UI must identify the simulation clearly.

## Target geometry
Primary target: **1920×1080**, 27-inch Full HD; start maximized with Windows taskbar intact. Minimum supported app geometry: 1100×650. Panels use adjustable sashes. Fonts: Segoe UI for UI text, Consolas for monospaced diagnostics/code, roughly 10–12pt code. No mouse-wheel-only action is necessary. Keyboard: F5 play/pause, F6 warning, F7 build, F11 fullscreen, Escape exit fullscreen, Ctrl+R reset.

## Hierarchy / static wireframe

```
┌──────────── application identity · Windows x64 ────────── SIMULATION ────┐
│ [Pause] [Build] [Warning] [Failed build] [Reset]      Mode | Speed      │
├───────────────┬─────────────────────────────────────┬──────────────────┤
│ EXPLORER      │ tab: runtime_engine.cpp             │ DIAGNOSTICS      │
│ workspace     │ C++23 code with syntax colors       │ warnings/errors  │
│   src/core    │ animated typing/scrolling           │ analysis         │
│   src/render  │                                     │                 │
│   include/... ├─────────────────────────────────────┤ simulated CPU   │
│ Outline       │ TERMINAL / OUTPUT                   │ simulated RAM   │
│               │ staged build/warning/test events    │                 │
├───────────────┴─────────────────────────────────────┴──────────────────┤
│ status | builds | simulation-only                   Ln / Col  UTF-8      │
└────────────────────────────────────────────────────────────────────────┘
```

## Colors and visual motion
Background #0c111b; panels #111827 / #121c2a; editor #0f1624; C++ keywords purple #c6a0f6; functions/types blue #69b5ff; strings green #5fd59c; warnings yellow #e8bd6c; errors red #f77987. Motion is localized to the editor, terminal, indeterminate build progress, and simulated performance readouts; no flash storms, no fake system alerts, no actual CPU overload.

## Behavioral contract
- Play starts automatically; pause freezes the simulator without clearing state.
- Build stages compile lines, optional warning, link and test summaries; error build ends in FAILED without fake PASS.
- Warning injects a nonfatal problem and increments the live issue counter.
- Reset restores initial simulated project state.
- Mode Intensiv increases warnings; Speed 0.5×/1×/2×/4× controls animation frequency.
- Interactive explorer selection changes viewed synthetic file only.
- Source snippets are synthetic and illustrative, not intended to compile together.
- Engine deterministic when initialized with the same seed; tests exercise success/failure and reset.

## Branding boundary
The `125A-Branding` README and official master SVG were inspected. v0.1.0 **does not reproduce or redraw the 125A logo**; it only displays the project's textual name. If logo artwork is introduced, the original official vector must be reused proportionally, without altering the red stroke or recreating lettering.

## Acceptance gates
1. Static syntax/tests execute on target Python.
2. Windows PyInstaller `--onefile --windowed` creates actual `.exe`.
3. Built EXE returns success for `--self-test` without creating any desktop window.
4. User checks the visible UI on Windows 11 at 1920×1080, keyboard shortcuts, pane dragging, warning/error flows, screen sizing, responsiveness and exit. CI success does not imply desktop/UX acceptance.

# 125A Fake IDE

**A fully animated, realistic-looking fake programming environment for Windows.** It is a harmless desktop simulator for entertainment: it does **not** compile C++, edit real code, execute build commands, inspect actual CPU/RAM, collect data or communicate with the internet.

## Download the Windows EXE

After the first successful [Windows Build workflow](../../actions/workflows/windows-exe.yml), open the workflow run, download the **125A-Fake-IDE-Windows-x64** artifact under *Artifacts*, unpack it and start `125A-Fake-IDE.exe`. GitHub requires login to download workflow artifacts. The EXE is built using Python/Tkinter and packaged with PyInstaller (no Python installation needed for normal use).

## What it shows

- Windows-style dark developer workspace, C++23 source tabs and syntax highlighting.
- Animated code typing, auto-navigation among six synthetic files and a project tree.
- Fake incremental MSBuild compilation, linked EXE and simulated 18-test regression suite.
- Warning/Error diagnostics, optional deliberately failing build, and live fake CPU/RAM readouts.
- Adjustable animation speed, normal/intensive mode, responsive split panes and fullscreen.

**SIMULATION MODE / NO REAL BUILD** remains visible on screen. The logs, warnings, code, telemetry and tests are fictional.

## Controls

| Control | Action |
|---|---|
| F5 | Pause/continue |
| F6 | Inject simulated warning |
| F7 | Start simulated build + tests |
| Error-Build button | Trigger deliberately failing build |
| F11 | Fullscreen on/off |
| Escape | Exit fullscreen |
| Ctrl+R | Reset session |
| Explorer tree | Show a different fake source file |
| Speed selector | 0.5×, 1×, 2×, 4× |
| Mode selector | Normal, Intensiv (more warnings) |

## Development

Requires Python 3.11+ (built and CI-tested on Python 3.13). From repository root:

```powershell
python -m unittest discover -s tests -v
python src/main.py
```

For a local Windows EXE:

```powershell
python -m pip install pyinstaller==6.16.0
python -m PyInstaller --onefile --windowed --clean --name 125A-Fake-IDE --paths src src/main.py
```

The output will be at `dist/125A-Fake-IDE.exe`.

## Development status

**v0.1.0 — initial development candidate.** Unit tests can be run without a GUI. The Windows workflow builds and self-tests the EXE, but a real **Windows 11, 1920×1080 visual/interaction review** is separately required before saying the visual UI is accepted. Product wireframe and scope are documented in [docs/DESIGN.md](docs/DESIGN.md).

## Engineering policy

The project follows the applicable repository/workflow, GUI and QA standards in [`125A-Engineering`](https://github.com/challanger2000/125A-Engineering). The official brand logo was not recreated or substituted. No audio/DSP or VST3 technology is involved.

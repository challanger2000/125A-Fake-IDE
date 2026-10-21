# 125A Vibe Coding Edition (v0.2.0)

An animated Windows desktop IDE parody about **Vibe Coding**: confident AI replies, a failing compiler, rising issue counts, rollback loops, and occasional staged application crashes. The visuals are deliberately serious-looking.

This is a theatrical offline program, **not** a working coding environment. It does not compile source code, modify projects, contact Anthropic/Claude, read user files, use real system performance metrics, or intentionally crash the Windows process. The Claude panel is **scripted parody text**, not a real AI connection or a representation of Anthropic software. No official logos are used.

## Windows EXE

Run the [Windows EXE workflow](../../actions/workflows/windows-exe.yml) and download its `125A-Fake-IDE-Windows-x64` artifact for the `develop/v0.2.0` branch. Unzip and run `125A-Fake-IDE.exe`. Python installation is not needed for the packaged EXE.

## Features

- Full-screen, dark Windows developer workspace optimized for 1920×1080 monitors, with F11 and Escape.
- Animated C++ code editing, source tree, syntax highlighting, incremental build terminal, test results, warnings, and errors.
- **Claude assistant** pane that confidently claims success regardless of the compiler's actual output.
- **Vibe Backlog** with familiar plugin-development bugs and a growing issue count.
- Modes: **Normal** (quiet), **Vibe** (default, escalating errors), **Panik** (more frequent incidents and staged crashes).
- Real-looking application error **overlay** and safe automatic recovery after about six seconds; manual recovery button.
- Optional forced error build, warning generation, pause, restart and change of animation speed.

## Keys

| Key | Action |
| --- | --- |
| `F5` | Pause / resume |
| `F6` | Inject warning |
| `F7` | Start a (fictional) build |
| `F8` | Switch Vibe / Panik mode |
| `F9` | Trigger a staged crash and automatic recovery |
| `F11` | Toggle borderless fullscreen |
| `Esc` | Exit fullscreen |
| `Ctrl+R` | Reset all stage counters and fake output |

Staged crashes never intentionally terminate the EXE, and automatic recovery resumes the scene. In Normal mode, no automatic crashes are triggered, but the F9 button remains available.

## Development and verification

Requires Python 3.11 or newer for development; Windows CI uses Python 3.13 and PyInstaller.

```powershell
python -m unittest discover -s tests -v
python src/main.py
python src/main.py --self-test
```

The GitHub Actions Windows workflow runs compile checks, Python tests, EXE packaging and a no-GUI smoke test. A live Windows 11 full-screen and interaction check remains an independent acceptance step. A preview from Linux/Xvfb does not establish Windows GUI acceptance.

## Project policy

Uses the existing approved `develop/v0.1.0` source as its base and develops on `develop/v0.2.0`. New GUI visuals are original, no 125A brand logo artwork was recreated, and no VST3/DSP code is involved. Applicable 125A Engineering repository rules continue to apply.

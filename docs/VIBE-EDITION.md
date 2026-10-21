# Vibe Coding Edition – design contract

- Exact target: Windows 11, 1920×1080, full-screen and resizable modes.
- Main title: **125A / VIBE CODING EDITION**. The UI presents the scenario seriously, without explicit FUN/FAKE/SIMULATION panels.
- Left: project tree and plugin-development backlog; center: C++ editor and compiler output; right: scripted "Claude" chat, problems and runtime readings.
- Humour is visual contradiction: green AI confidence versus red build output and renewed open issues.
- Simulated crashes are deterministic, user-visible **GUI overlays**. Do not throw uncaught exceptions, crash a subprocess, execute actual compiler commands, contact a third-party API or access project files.
- Recovery can be user-initiated or automatic after 6200ms. Recovery must not duplicate timers, persist an overlay, or swallow F11/Escape.
- Controls: F5/F6/F7/F8/F9/F11/Escape/Ctrl+R and toolbar alternatives. F11 must work while code editor is focused.
- Never mislabel fake simulation results as actual Windows/Studio One/VST3 test evidence. Product documentation must plainly disclose the simulated nature outside the in-character main UI.
- No Anthropic trademarks beyond textual satirical name references; no impersonation of a real connected product.

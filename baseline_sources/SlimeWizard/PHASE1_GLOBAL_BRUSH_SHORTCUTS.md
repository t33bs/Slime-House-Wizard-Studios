# Phase 1 — Global brush size shortcuts

- + and = increase the active painting tool's brush size; - decreases it.
- Shortcuts use Qt ApplicationShortcut context to work when focus moves across the editor.
- Slime Cleaner and Slimer maintain separate 1–32 pixel brush sizes.
- Neither tool active: shortcut does nothing.
- Windows GUI verification remains necessary, including keypad +/- and focus inside spinboxes.

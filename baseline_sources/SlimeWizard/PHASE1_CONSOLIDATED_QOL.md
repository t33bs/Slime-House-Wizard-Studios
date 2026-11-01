# Phase 1 consolidated quality-of-life implementation

Implemented in friendly_animator.py:
- Move Original Pixels checkbox (checked by default); uncheck for Copy Pixels.
- Move clears selection mask from visible active-pose source layers at placement; copy preserves originals.
- A separate Slimer Preview panel displays transformed selected pixels, updating through the regular refresh path.
- Existing highlight color selection and + / - highlight brush shortcuts remain.
- Slime Cleaner uses the independent erasing tool and synchronizes originals in the current source.

Still requires Windows GUI verification: correct Slimer move/copy and undo, exact RGBA preservation, preview appearance and responsiveness, Slime Cleaner stroke behavior, brush hotkeys, selection highlight color, and timeline isolation. Do not treat automated model tests as GUI signoff.

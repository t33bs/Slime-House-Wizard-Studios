# Slimer Tool — Phase 3

Built on the Phase 2 source snapshot; original Windows portable and installer GitHub Actions workflow retained.

## Added
- Toggle between brush painting and mouse-driven transform mode.
- Drag to move selected pixels; Shift+drag changes scale; Alt+drag changes rotation.
- Separate selection-mask undo and redo controls, with one stroke per history step.
- Clearer active-state button styling in the existing charcoal/slime-green theme.
- Existing Place Frame, Place as Layer, and model-history undo/redo remain in place.

## Known follow-up work
- Run the PySide6 GUI on Windows and test coordinate mapping and drag responsiveness.
- Connect selection history to Ctrl+Z/Ctrl+Y contextually, and make transform gestures single undoable actions.
- Add visible mouse handles and a dedicated custom slime cursor.
- Finish Move Original behavior and test export/save-reopen after placement.
- Build Windows portable and installer artifacts in GitHub Actions.

## Verification
- `python -m compileall -q friendly_animator.py studio`
- `python -m unittest discover -s tests -q` — 140 tests passed in this environment.

# Slime Wizard Phase 77 — Collapsible Transform Handles ON the Canvas

## What changed

- The **Transform handles** control is a small overlay in the top-right corner of the actual canvas, **not a new menu in the left panel**.
- The overlay is **collapsed by default**. Expand it to choose an Asset Library layer and a handle mode: **X — Move horizontally**, **Y — Move vertically**, or **R — Rotate in degrees**.
- **Only one handle is rendered and hit-testable at a time**. Changing the menu does not alter artwork, create layers, modify animation frames, or commit a move.
- The existing **Edit Selection** button still creates a layer from highlighted pixels (one step) and enables/disables its handles. It does **not** reintroduce Finish Selecting.
- The selected layer in the canvas dropdown stays synchronized with the Asset Library. During a staged Move Original/Copy transaction the layer dropdown is locked, preventing accidental source switching.
- The existing exact-degree controls remain available. Free drag on selected art still works for moving both axes; the on-canvas chosen handle gives axis-restricted move or rotation.
- Nothing about the handle overlay is baked into exported PNG/GIF/APNG artwork.

## Invariants

- Move Original Pixels defaults ON. Source erasure occurs **only** when Apply Move succeeds, never when a layer is created, a handle mode is changed, or the menu is expanded/collapsed.
- Copy Pixels remains available, and Cancel does not erase source artwork.
- No auto-added animation frames, no source loss, no GitHub changes.

## Tests

Headless regression suite: `PYTHONPATH=. python -m pytest -q`.

Windows PySide6 GUI checks in the project folder using the previously configured venv:

```powershell
& "$env:USERPROFILE\Downloads\DocumentsSlime-Wizard-Pre-Merge-Backup\.venv\Scripts\python.exe" -m pytest -q tests/test_phase77_canvas_handle_menu_gui.py tests/test_phase76_asset_handles_gui.py tests/test_phase75_staged_rotation_gui.py tests/test_phase74_one_button_edit_selection_gui.py
```

Then launch the program on Windows and verify: highlight → Edit Selection → expand **Transform handles** directly on canvas → choose R → rotate → Apply Move, with no loss of source pixels until the final apply. Select a different layer after Apply or Cancel, then verify X and Y modes separately.

The headless environment cannot run PySide6. GUI tests are included but require Windows verification.

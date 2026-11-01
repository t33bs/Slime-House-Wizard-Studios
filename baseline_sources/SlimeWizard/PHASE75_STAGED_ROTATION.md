# Phase 75 — Rotate the Slimer Asset after Edit Selection

## User-reported problem

Phase 74's one-button Slimer workflow successfully created a draggable Asset Library layer. However, it was difficult to rotate the layer in degrees: the full-canvas transparent layer's blue rotation handle was positioned far away from the selected pixels, and `Slime rotate °` still changed the old floating-selection preview rather than the newly staged asset.

## Fix

- Preserve **Highlight → Edit Selection → Transform → Apply Move**, with no additional Finish Selecting or Move Selection button.
- New Slimer layers keep their full-canvas source-image representation, but get a rotation pivot at the **center of the selected visible pixels**, not the full canvas center.
- The existing blue rotation handle is drawn beside the selected artwork and hit-tested at that same location. It can be dragged to rotate; **Alt+drag** over the staged artwork also rotates it.
- Both existing angle controls (`Turn part (degrees)` in the Asset Library and `Slime rotate °`) now rotate the staged editable layer. They stay synchronized.
- Move Original Pixels remains **ON by default**. It never erases source artwork during highlight, layer creation, movement, or rotation; **Apply Move** first checks destination safety, then erases the selected source pixels atomically. Copy Pixels and Cancel preserve the source.
- No extra frames, new steps, new buttons, or destructive commits before Apply Move.
- Rotation safety preflights remain enforced: dangerous off-canvas rotation of Move Original is rejected rather than losing pixels.

## Test status and limitations

- Full non-GUI regression tests must pass before release.
- Windows PySide6 GUI tests (`tests/test_phase75_staged_rotation_gui.py`) verify degree spinners, asset pivot and handles, mouse dragging, applying Move Original / Copy Pixels, cancel safety and frame count. Run using the existing PySide6 6.12 environment; GUI tests cannot run in the current Linux Python environment without PySide6.
- This is a proposed **Phase 75**, pending Windows hands-on acceptance; do not call it production-proven until the Windows GUI and real Swordcat sprite checks pass.

## Windows command

From the extracted Phase 75 folder:

```powershell
& "$env:USERPROFILE\Downloads\DocumentsSlime-Wizard-Pre-Merge-Backup\.venv\Scripts\python.exe" -m pytest -q tests/test_phase75_staged_rotation_gui.py tests/test_phase74_one_button_edit_selection_gui.py tests/test_phase73_edit_selection_button_gui.py
```

GitHub untouched.

# Phase 74 — Single-step selection-to-layer workflow

User-approved UX: do **not** reintroduce Finish Selecting, and do not replace it with a separate Move Selection button.

Visible workflow: **Highlight pixels → Edit Selection (Create & Move Layer) → drag / edit real layer → Apply Move**.

Changes:
- Hide the legacy floating-selection drag toggle (preserved internally for compatibility with older regression tests).
- Edit Selection now ends highlighting, creates and selects the real editable asset, and automatically switches the canvas from highlight brushing to normal asset dragging.
- Pending layer is no longer covered by the highlight tint; normal asset selection indicators remain.
- Apply Move and Cancel restore highlight brushing automatically. Move Original Pixels remains checked by default; Copy Pixels remains available by unchecking before staging.
- Move Original Pixels stays checked by default, is captured for the staged selection, and only erases the selected original pixels when Apply Move succeeds. Copy Pixels keeps the source intact. The mode is locked while a layer is pending so the user cannot accidentally switch policies mid-move. No automatic pose/frame is created.
- Update the button name and tooltip; clean up a stale Finish Selecting status string.
- Add GUI regression tests for Move Original, Copy Pixels, Cancel, missing selection, draggable selection, no automatic new frame.

Validation: source compilation and non-GUI regression suite run in this environment; Windows PySide6 GUI tests must also pass before treating as fully verified.

Run on Windows from project directory:
`& "$env:USERPROFILE\Downloads\DocumentsSlime-Wizard-Pre-Merge-Backup\.venv\Scripts\python.exe" -m pytest -q tests/test_phase74_one_button_edit_selection_gui.py tests/test_phase73_edit_selection_button_gui.py`

GitHub untouched.

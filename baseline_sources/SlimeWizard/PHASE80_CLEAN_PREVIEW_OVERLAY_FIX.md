# Phase 80 — Clean Slimer Preview buffer fix

## Windows defect reproduced by user

Phase 79 PySide6 focused gate reported `1 failed, 3 passed`: `test_clean_slimer_preview_matches_live_render_without_canvas_tool_overlays` failed because preview pixel showed green `#00cc33` instead of the original selected leg's orange `#f05023`.

## Cause

`refresh()` assigned both `composed` (editor image) and `live_render` (clean preview) to the same PIL Image object. When Slimer selection tint was added with in-place `composed.alpha_composite(tint)`, the green selection overlay contaminated `live_render` and was shown in Slimer Preview. Joint dots and floating selection overlays had the same potential aliasing issue.

## Fix

`live_render` remains an untouched model render; when an editor-only operation would mutate `composed`, it is copied once *only if* it still aliases `live_render`. This avoids unconditional full-canvas copies when there are no overlays. Onion-skin already generates a separate image. The Slimer Preview and the existing Frame Preview receive `live_render`, while `canvas.set_art` receives the editor composite. No Slimer source pixels or layers are modified by this fix.

## Regression tests

- Existing Windows gate: `tests/test_phase78_zoom_handle_and_clean_preview_gui.py` (the user-reported failure).
- Added Windows gate: `tests/test_phase80_clean_preview_buffer_gui.py` with full-pixel comparison for selection tint and joint dot guides.
- Also retain Phase 79 toolbar/canvas layout GUI gate.

Commands from extracted Phase80 folder in Windows PowerShell:

```powershell
& "$env:USERPROFILE\Downloads\DocumentsSlime-Wizard-Pre-Merge-Backup\.venv\Scripts\python.exe" -m pytest -q tests/test_phase80_clean_preview_buffer_gui.py tests/test_phase78_zoom_handle_and_clean_preview_gui.py tests/test_phase79_toolbar_buddy_gui.py
```

Move Original Pixels remains checked by default; Apply Move remains responsible for source erasure; Copy Pixels, existing transforms, poses, exports, and GitHub are untouched.

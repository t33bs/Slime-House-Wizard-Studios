# Phase 79 — Slime Wizard canvas space cleanup

## User-requested result

In the main workspace, remove the redundant Slime Buddy station selection dropdown (Import/Assembly/Rigging/Poses/etc.) and Check animation readiness button entirely. Bring the **existing** Slime Buddy ON/OFF toggle up to the top toolbar and let the canvas fill the freed height.

## Implementation details

- `friendly_animator.py` creates `buddy_toggle` as `topSlimeBuddyToggle` in the Easy Mode / Undo / Redo toolbar, with the saved `QSettings` value unchanged.
- The middle layout no longer creates `buddy_station`, `check_button`, extra guidance labels or associated rows. After the internal hidden animation selector, the single header is followed immediately by the editing canvas.
- Slime Buddy's optional guidance remains inside the right preview-dock speech bubble; it automatically describes import, normal posing or Slimer editing depending on context. No creative judgments.
- The right dock ON checkbox remains connected bidirectionally to the top toggle. The bubble/mascot reflect saved state immediately on startup, including when OFF.
- `show_technical_checks` and `studio/technical_checks.py` remain available internally to prevent unrelated regressions; only the redundant user-facing button was removed. Import PNG assets remains in the main top toolbar.

## Verification

Local (no PySide6): `python -m pytest -q` => **469 passed, 26 skipped, 12 subtests passed**. `python -m py_compile friendly_animator.py` passed. ZIP integrity passed.

Windows PySide6 test command from the extracted Phase79 folder:

```powershell
& "$env:USERPROFILE\Downloads\DocumentsSlime-Wizard-Pre-Merge-Backup\.venv\Scripts\python.exe" -m pytest -q tests/test_phase79_toolbar_buddy_gui.py tests/test_phase78_zoom_handle_and_clean_preview_gui.py
```

Manual acceptance: the central panel should start at its `STEP 2` label with canvas immediately beneath; no Import/Assembly/Rigging dropdown or Check animation readiness button above it. The Slime Buddy ON/OFF checkbox is in the upper toolbar, can be turned OFF/ON, and the right dock mirrors it. Confirm canvas is taller; still able to Highlight -> Edit Selection -> Transform -> Apply Move.

Never changed GitHub; preserve Move Original Pixels ON by default, Copy Pixels, Apply Move-only source erasure, and independent poses.

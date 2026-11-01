# Phase 84 — Yellow editor joint-guide visibility (2026-10-30)

## Report and root cause

After a successful Slimer move, the user saw a **yellow square/knob** on the Swordcat's leg. It was **absent from Slimer Preview and Frame Preview**. The earlier Phase 83 explanation incorrectly attributed it to the green dashed highlight outline. These are different guides.

`Suite.refresh()` iterated over `model.anchors` and drew a small yellow circle into the *editor-only* RGBA composite on **every refresh**. `slimer_create_editable_layer()` automatically assigns each new Slimer layer a rotation pivot in `model.anchors`, so the yellow guide persisted after Apply Move even when the canvas Transform menu reported `Handles OFF`.

## Fix

- Only draw yellow joint-dot guides in the canvas compositor while **Place a joint dot** mode is actively enabled (`canvas.anchor_mode`).
- Refresh immediately when the joint-placement button is turned on/off, showing or hiding guides without modifying artwork.
- Preserve stored anchor coordinates and rotation pivots. Neither Slimer source-erasure rules nor Apply Move logic changes.
- Previews and exports remain clean and contain no tool overlays. The X/Y/R handles remain governed by the on-canvas Transform menu.

## Verification

- Local `python -m pytest -q`: **481 passed, 33 skipped, 12 subtests passed** (new GUI tests skipped because PySide6 is not installed here).
- Added `tests/test_phase84_joint_guide_visibility_gui.py`: verifies yellow joint marker only appears while placing a joint; checks that newly created Slimer layer keeps a rotation pivot but has no yellow guide after Apply Move and pixel-for-pixel matches clean model render.
- Python compilation and ZIP integrity verified.

## Windows PySide6 test

From the extracted Phase 84 folder:

```powershell
& "$env:USERPROFILE\Downloads\DocumentsSlime-Wizard-Pre-Merge-Backup\.venv\Scripts\python.exe" -m pytest -q tests/test_phase84_joint_guide_visibility_gui.py tests/test_phase83_repeat_source_focus_gui.py
```

Then launch `friendly_animator.py`, move a leg via Slimer and Apply Move; verify the yellow knob vanishes, and that selecting the **Place a joint dot** tool temporarily shows the joint guide. Recheck repeated Slimer selection and source safety separately: Phase 84 does not claim to resolve all rejected Move Original selections.

No GitHub changes.

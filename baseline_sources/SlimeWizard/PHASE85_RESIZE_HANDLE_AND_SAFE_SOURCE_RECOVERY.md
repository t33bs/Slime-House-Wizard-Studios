# Phase 85 — Resize Selected Assets + Safe Second-Selection Recovery

## Problem report (October 30–31, 2026)

- User confirmed **Phase 84's yellow joint-dot marker now disappears after Apply Move**. Retain the pivot internally; show joint guides only while Place a Joint Dot is active.
- User could not **resize the currently selected asset**. On-canvas handle selector had only X, Y, Rotation; the left `Slime size %` control adjusted an obsolete highlight preview after Edit Selection had already created a real Asset Library layer.
- On a later highlighted Move Original selection, the app refused source erasure: "some pixels are translucent or overlap other layers." This is a source-safety check, not evidence the one-button workflow is stuck. It must not silently erase selected semitransparent or multiply-owned pixels.

## Changes

- Add an `S — Resize artwork` option to the existing **collapsible, on-canvas Transform handles** menu. Still only one handle at a time; no new left-sidebar buttons.
- Draw and hit-test the same reachable, zoom-aware resize handle as other modes; drag adjusts the existing `Slime size %` control.
- When an Asset Library layer is being edited, `Slime size %` now changes that real layer (previously it changed only the old float/highlight preview). Reset to `100%` at the start of each layer editing session.
- For Slimer's **full-canvas transparent PNG layers**, resample just the actual selected artwork around its stored pivot using nearest-neighbor; keep original 128x128 layer coordinates so the existing Move Original source-erase and rotation contracts remain intact. Reject resizing that would clip the selection instead of quietly losing pixels.
- Recalculate percentages from a stable per-session source to avoid repeated-resampling degradation. Ordinary imported PNGs use their edit-start width and height and preserve their original source image.
- Keep Edit Selection as the single transition: Highlight → Edit Selection → choose transform including Resize → Apply Move; no automatic frame creation.
- No change to the conservative Move Original erasure policy: selection of fractional-alpha pixels or ambiguous overlapping source provenance can be rejected without modifying artwork. Clear Selection and edit an existing asset as a whole, or uncheck Move Original for Copy Pixels, or select only safe opaque, unobstructed pixels.

## Local checks

- `python -m py_compile friendly_animator.py studio/slimer_asset_scale.py` passed.
- Qt-free regression suite: **485 passed, 34 skipped, 12 subtests passed**. PySide6 is unavailable in this workspace; new GUI tests require Windows environment.
- Added `tests/test_phase85_selection_scale_headless.py` for raster scaling, alpha preservation, 100% restore, and no-clipping guards.
- Added `tests/test_phase85_resize_and_selection_recovery_gui.py` for staged Slimer resize + Apply Move, imported asset resize, and recovering from a translucent selected-pixel rejection without discarding source pixels.
- Updated older Phase 76/77 tests to retain the original X/Y/R checks and recognize the new Resize option.

## Windows verification command

From the extracted Phase 85 directory in PowerShell:

```powershell
& "$env:USERPROFILE\Downloads\DocumentsSlime-Wizard-Pre-Merge-Backup\.venv\Scripts\python.exe" -m pytest -q tests/test_phase85_resize_and_selection_recovery_gui.py tests/test_phase84_joint_guide_visibility_gui.py tests/test_phase83_repeat_source_focus_gui.py
```

## Manual acceptance

1. Open Swordcat with one **opaque region**. Highlight → Edit Selection. Expand on-canvas Transform handles and choose `S — Resize artwork`.
2. Drag S to resize, or enter 150 in `Slime size %`. Verify selection grows around its artwork pivot rather than magnifying transparent 128x128 padding. No pixels disappear from source before Apply Move.
3. Click Apply Move. Verify selected source pixels disappear, transformed destination remains, handles and yellow joint guides disappear, no frame is created.
4. Highlight a different **opaque, unobstructed** region; repeat on the *same pose* without resetting Slimer.
5. When highlighting translucent/overlapping artwork, ensure a blocked Move Original selection leaves artwork unchanged. Clear Selection, select the complete layer in Asset Library, click Edit Selection, and edit its placement or size without a duplicate layer or frame.
6. Import a small PNG asset; choose it in Asset Library → Edit Selection → Resize 150% → Apply Move. Verify native source and visual transparency are preserved.

GitHub remains untouched.

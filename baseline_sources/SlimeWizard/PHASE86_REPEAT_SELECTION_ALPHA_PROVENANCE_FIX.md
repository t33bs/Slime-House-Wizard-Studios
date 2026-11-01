# Phase 86 — Repeat Slimer Selection: Exact Alpha-Presence Safety Fix

## Report and verification (October 30–31, 2026)

After Phase 85's 7 Windows PySide6 tests passed, the user confirmed selected-artwork resize and Apply Move worked on real Swordcat art. However, after the first successful Move Original, the second highlight could not become an editable layer, even when choosing a different original Swordcat PNG with legs farther apart. This is **not resolved merely by returning Slimer to brush mode**.

## Root cause found

In `_slimer_layered_erase_plan`, a binary 0/255 selected-pixel mask was compared with the raw *fractional* alpha mask for the currently visible artwork. `ImageChops.subtract(selected, visible)` reported a positive difference at any selected pixel with alpha between 1 and 254, incorrectly treating it as invisible/unmapped even when there was a single clear source layer. A normal highlight brush can touch a sprite's antialiased/partially transparent edges even when the user targets a visually opaque section.

## Fix

- Compare selected pixels against **binary alpha presence**, not raw alpha magnitude. This avoids false rejection of isolated translucent source pixels.
- Allow moving translucent pixels **only when no other underlying visible asset contributes at those same selected positions** and the source mapping is complete, exact, and editable. Preserve the original RGBA alpha in both the new selection and the source erase transaction.
- Continue rejecting composited translucent-over-other-layer pixels, partial footprints of scaled nearest-neighbor pixels, stale source buffers, destination clipping, or invalid staged transactions. Never bypass rollback or preflight.
- When Move Original is blocked, display concise diagnostic counts: `selected`, `translucent`, and `multi-layer`. These are observations, not blanket permission decisions. The artwork stays unchanged on failure.
- Preserve default checked Move Original, optional Copy Pixels, the single Edit Selection button, the on-canvas X/Y/R/S picker, independent layers and saved poses, the yellow joint-dot cleanup, and **no new frame** while editing.

## Tests

- Added Qt-free `tests/test_phase86_safe_translucent_repeat_model.py`: isolated partial-alpha move preserving pixel RGBA, genuine overlap rejection, unrelated lower-layer translucency, partial scaled-source rejection, and a second move after a transformed previous Slimer layer.
- Added Windows/PySide6 `tests/test_phase86_repeat_alpha_gui.py`: resize/apply first opaque selection then highlight/stage/apply second mixed-alpha source on same pose without reset or new frame; second test verifies blended multi-layer source remains rejected with useful diagnostic.
- Updated older Phase 15 regression expectations where they intentionally rejected *all* translucent selections; retained fallback and actual overlap rejection tests.
- Updated Phase 83 and Phase 85 Windows negative tests to use real overlapping fractional-alpha layers, since a standalone fractional-alpha pixel is now intentionally supported. They still verify failure leaves artwork untouched and that editing a whole existing layer recovers normally.
- Qt-free full suite: **490 passed, 35 skipped, 12 subtests passed**; PySide6 unavailable in this execution environment, so user must run Windows GUI gates.

## Windows verification

Extract the ZIP, open PowerShell in the extracted Phase 86 folder and run:

```powershell
& "$env:USERPROFILE\Downloads\DocumentsSlime-Wizard-Pre-Merge-Backup\.venv\Scripts\python.exe" -m pytest -q tests/test_phase86_repeat_alpha_gui.py tests/test_phase85_resize_and_selection_recovery_gui.py tests/test_phase83_repeat_source_focus_gui.py
```

Then launch the app:

```powershell
& "$env:USERPROFILE\Downloads\DocumentsSlime-Wizard-Pre-Merge-Backup\.venv\Scripts\python.exe" .\friendly_animator.py
```

On the SAME pose with Move Original checked, highlight one section -> Edit Selection -> resize/move -> Apply Move. Then highlight another section of the original, including an edge pixel, -> Edit Selection -> move -> Apply Move. Confirm source erasure only at Apply, original and moved pixels are intact, no extra frame, and handles disappear. If a selection is refused, send its exact new `selected/translucent/multi-layer` numbers; do not reset or change to Copy as a substitute for diagnosing a valid source.

GitHub remains untouched. This is a candidate fix, pending Windows PySide6 + actual artwork acceptance.

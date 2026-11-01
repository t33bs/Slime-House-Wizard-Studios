# Phase 94 — Edit Selection active visual cue

**Status:** Candidate for Windows GUI verification; user-reported Phase 92/93 cross-pose overwrite blocker remains pending manual acceptance.

## Requested change
Keep `Edit Selection • Create / Show Handles` visibly **lit up while the canvas's editable transform handles are active**. Return to the normal button appearance whenever handles are hidden or editing is finished. This change is presentation-only.

## Implementation
- `friendly_animator.py`: `_show_asset_transform_controls()` now controls a bright-green button fill, neon-green outline, bold white label, and boolean `editingActive` property from the real `canvas.asset_controls_enabled` state.
- The button remains a *command button*, not a separate checkable toggle. A failed Edit Selection click does not falsely turn the light on.
- Existing text behavior (`✓ Edit Selection • Hide Handles`) and the one-button Slimer workflow are unchanged.
- UI state is cleared through existing paths (`slimer_clear`, Apply Move, Cancel, explicit hide, pose/project resets).
- No changes to image pixels, layers, source erase, Move Original/Copy, pose persistence, reference features, Slime Cleaner, or GitHub.

## Tests
- New `tests/test_phase94_edit_selection_active_gui.py` (Windows PySide6, autosave recovery isolated):
  1. Paint → Edit Selection lights up → hide/reopen handles → Apply Move turns it off without pixel loss.
  2. Direct editing of an existing Asset Library layer lights up and turns off, without adding layers.
  3. Rejected Edit Selection does not illuminate.
- Local available full suite: **497 passed, 42 skipped, 12 subtests passed**, no failures. PySide6 GUI tests skip locally because PySide6 is not installed.

### Windows PowerShell targeted command

```powershell
& "$env:USERPROFILE\Downloads\DocumentsSlime-Wizard-Pre-Merge-Backup\.venv\Scripts\python.exe" -m pytest -q tests/test_phase94_edit_selection_active_gui.py tests/test_phase93_pose_identity_gui.py tests/test_phase91_no_reference_gui.py tests/test_phase88_first_place_frame_gui.py tests/test_phase87_pose_merge_gui.py tests/test_phase86_repeat_alpha_gui.py
```

**Expected:** 11 passed (Phase 94 adds three to the previous 8). Real Swordcat manual validation still required, especially the previously reported pose-overwrite problem after Place Frame.

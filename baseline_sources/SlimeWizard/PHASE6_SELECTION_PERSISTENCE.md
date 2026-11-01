# Phase 6 — Edit Selection persistence audit and targeted fix

Audited the existing Edit Selection toggle: it already retains the active mask and transform when toggling between highlight and floating selection. No duplicate toggle implementation was added.

Fixed a genuine adjacent issue: switching color tabs discarded Slimer Undo/Redo stacks. Each color tab now retains independent Undo/Redo history alongside its mask and transformation values. Reset paths for tool activation, clear, and project changes clear the per-tab history safely. Added `tests/test_phase6_selection_history.py` to exercise switching between tabs and returning to earlier edits without PySide6.

## Deferred Windows GUI checks
- Edit Selection repeatedly without losing highlights, transforms, or source pixels.
- Alternate Start/Middle/End/custom tabs; verify Undo/Redo history is scoped to the selected tab.
- Verify selection preview only appears after Finish Selecting.
- Confirm All Placements with multiple color tabs, both Move Original and Copy Pixels.
- Confirm clearing or switching projects cannot restore stale selection history.

## Next roadmap item
Phase 7 — right-side Slimer Preview: already implemented; audit for any real gap before modifying. Phase 8 — UI cleanup follows.

# Slime Wizard Phase 83 — repeat selection and editor-handle clarity

## User's Phase 82 observation

A real Swordcat could be moved once using Move Original, but a later highlighted green region refused to make another layer. The screenshot's message was **"Selected pixels cannot safely be moved from their source layers. Artwork unchanged."** The canvas also showed a green dashed rectangle, while the Transform menu and active-layer label both said **Handles OFF**.

These are two different states: the rectangle was the **highlight-selection boundary**, not the X/Y/rotation handle; the source-erase preflight was rejecting a potentially unsafe destructive move. The source erase safeguards are intentionally retained. In particular, translucent or partially occluded source pixels, stale pose buffers, and incomplete resized-pixel footprints are not erased by assumption.

## Phase 83 changes

1. After successful **Apply Move**, turn off transform controls, return to a fresh Slimer highlight, and restore the Asset Library selection to the **source layer that was selected before creating the new Slimer Layer**. Use object identity, not a stale numeric index. No new frame, pose, or source erase is introduced by restoring selection.
2. Preserve the same source-layer recovery after Cancel, including when a staged layer was removed by another operation. Discard this transient pointer after undo, redo, project switch, and other project resets.
3. During the highlighting stage, show painted green highlights but **no dashed transform bounding rectangle**. The single chosen X/Y/R handle and its transform outline appear only in the editable-layer stage. This prevents a new highlight's outline looking like an old handle that failed to hide.
4. An unsafe Move Original selection now tells the user why it might be refused and offers an actionable, pixel-safe path: **Clear Selection → choose the existing layer → Edit Selection**, or uncheck Move Original to **Copy Pixels**. The original remains unchanged on rejection; no unsafe automatic Copy fallback is performed.

## Scope and limitations

- No extra Finish Selecting button, no new frame, no new step in the one-button flow.
- Move Original is still enabled by default; Copy Pixels remains optional.
- No weakening of source ownership, transparency, scaling or rotation safety checks.
- A selection of translucent or overlapping pixels can still be rejected by **Move Original**. This is not the same bug as stale GUI handles, and is not falsely reported as repaired. Use entire-layer repositioning or Copy Pixels for such cases.
- GitHub is untouched.

## Verification

- Available local pytest suite: **481 passed, 32 skipped, 12 subtests passed** (PySide6 GUI cases skipped here).
- Compile and ZIP integrity checks pass.
- New Windows test: `tests/test_phase83_repeat_source_focus_gui.py` verifies two distinct source-layer move cycles, source focus/handle cleanup, same-pose timeline integrity, and safe rejection with recovery instructions for translucent pixels.
- Structural UI test: `tests/test_phase83_no_legacy_outline.py`.

## Windows command

```powershell
& "$env:USERPROFILE\Downloads\DocumentsSlime-Wizard-Pre-Merge-Backup\.venv\Scripts\python.exe" -m pytest -q tests/test_phase83_repeat_source_focus_gui.py tests/test_phase82_repeat_and_imported_edit_gui.py tests/test_phase81_overlapping_move_gui.py
```

Then launch `friendly_animator.py`, test two **opaque** regions on the original Swordcat layer without resetting or adding a frame. If an additional green/translucent area refuses Move Original, read its specific status instead of resetting; test direct whole-asset Edit Selection or Copy Pixels as appropriate. Validate original pixels are never deleted on failed operations.

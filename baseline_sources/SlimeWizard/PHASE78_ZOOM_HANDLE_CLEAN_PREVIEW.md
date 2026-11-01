# Phase 78 — Reachable zoomed handles + clean Slimer Preview

## Symptoms (reported during Windows testing)
- The dashed asset outline could extend off-screen after even a small zoom, making the X/Y/R handle unreachable despite artwork still being visible.
- Slimer Preview showed only isolated highlight pixels, rather than the current artwork free of canvas editing overlays.

## Changes
- Introduced `studio/viewport_handles.py`: pure geometry keeps a selected layer's active X/Y/R affordance inside the widget (22px margin), adjacent to visible selected artwork, avoiding the floating Transform menu when possible. If artwork is wholly outside the widget, no stray handle is drawn. Natural on-screen handle positions remain unchanged.
- Both hit testing and painting call `DragCanvas._asset_handle_screen`, removing disagreement between what the user sees and can click. The dashed selection outline is thinner.
- Slimer Preview now renders `live_render` (clean live full canvas, including currently staged asset), not the isolated mask. Highlight tint, onion skins, anchor dots, and interactive handles stay only in the editor canvas; the Frame Preview remains independent for saved poses.
- Never altered Move Original default, delayed source erase, Copy Pixels, actual asset geometry or Apply Move transaction guards; no extra buttons added, GitHub untouched.

## Verification
- Headless geometry and source tests cover clipped zoom, menu avoidance, original affordance, and clean preview.
- Windows PySide6 GUI test `tests/test_phase78_zoom_handle_and_clean_preview_gui.py` covers staged source integrity, zoomed clickable X/Y/R, drag and rotation, clean preview pixels. This must run in the existing Windows venv; CI without PySide6 skips it.
- Manual gate: move or rotate an actual highlighted Swordcat leg when zoomed slightly and heavily; verify preview has no UI guides.

## Caveat
- The clean preview renders the current live scene before Apply Move; because Move Original deliberately delays source erasure, a staged layer may temporarily appear alongside source pixels until the move is confirmed. This preview does not simulate the destructive Apply Move transaction.

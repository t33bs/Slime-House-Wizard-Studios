# Phase 15 — Apply Move completion contract

`slimer_apply_move_to_pose()` now returns `True` only after the underlying
commit succeeds; missing selection, unfinished selection, and rejected source
preflights return `False`. The commit itself also returns `False` for an empty
selection. This makes a failed move distinguishable from a successful move
for future UI actions and regression tests, without bypassing any destructive
pixel safety check or creating a timeline frame.

A new GUI regression covers failed preconditions, successful move, exact
semi-transparent RGBA, selection reset, and unchanged frame count.

Windows GUI execution is still required: PySide6-dependent tests are skipped
in the current container. Do not replace the user's uncommitted working tree.

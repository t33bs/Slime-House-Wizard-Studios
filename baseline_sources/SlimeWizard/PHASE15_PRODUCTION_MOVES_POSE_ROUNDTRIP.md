# Phase 64 — Production Slimer operations through saved poses and project reopen

Adds `tests/test_phase15_real_moves_pose_save_roundtrip.py` to bridge a coverage gap: older save/reopen tests created Slimer-named layers directly, while the new tests invoke the actual `slimer_create_editable_layer` and `slimer_apply_move_to_pose` implementations before saving.

- Move Original Pixels: three consecutive selections, including moving pixels from a previously created Slimer layer; three independently saved poses, including later repositioning; save/reopen; navigate poses out of order and compare exact rendered RGBA bytes.
- Copy Pixels: two consecutive copies, then save/reopen and confirm the source and both copies are intact while the earlier pose remains isolated.
- The Qt editing-table integration remains Windows-only; these tests do not establish that GUI behavior is fixed.

No production source code changed. GitHub working tree was not touched.

# Phase 14 — Pose-source and visibility audit

The rendered pose may supply a per-pose `source_png` different from the mutable `parts[i][image]` buffer. Erasing by canvas mask against the latter can modify the wrong source. The destructive-move guard now rejects mismatched source buffers, while normal identical sources remain eligible. The erase loop now uses `resolved_pose()[i].visible` rather than the default part visibility.

This is a safety restriction, not a general inverse-rotation implementation. The exact nearest-neighbor rotation inverse remains deferred. Three focused headless tests cover mismatch, matching source, and inherited visibility. Windows GUI verification remains pending.

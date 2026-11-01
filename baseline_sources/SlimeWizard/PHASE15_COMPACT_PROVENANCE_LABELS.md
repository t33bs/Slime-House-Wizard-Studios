# Phase 63 — Compact source provenance mapping

Slimer's source mapping previously created a `list(range(1, sw*sh+1))` of Python integers every time it checked source ownership. On a 1024×1024 layer this is over a million Python integer objects in addition to Pillow's image buffer. This phase builds the same 32-bit integer labels with `array('i')` and `Image.frombytes`, retaining the original nearest-neighbor resize, paste, and rotate operations. The array uses native signed-integer byte order, matching Pillow's native `I` pixel mode.

New regression tests compare exact output bytes against the old implementation for scaling, clipping and rotation, and verify labels at 1024×1024. This is a memory/performance improvement to source mapping, **not** a confirmed fix for the Windows consecutive Slimer GUI bug.

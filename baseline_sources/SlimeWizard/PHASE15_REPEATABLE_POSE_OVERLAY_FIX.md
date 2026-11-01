# Phase 15: repeatable Slimer overlay moves — source consistency

A saved pose can restore the Slimer overlay's source buffer without updating the cached part image. Previous Move Original preflight rejected that valid selection; if bypassed, erasing from the cached image could edit pixels from the wrong pose.

Changes:
- Preflight accepts the dedicated Slimer overlay only if its resolved saved source and the active original buffer match byte-for-byte, it is unrotated, and its dimensions/position map exactly to the canvas.
- Erase uses the resolved pose-local source PNG rather than a potentially stale part image.
- All other source-safety checks remain in place. Copy Pixels remains supported.

Tests: 345 passed, 5 skipped, 441 subtests passed on Linux; Python compilation passed. The new check is static, not a GUI simulation. Windows end-to-end repeatable-move and frame-placement gates remain outstanding. Do not merge/replace the uncommitted Windows working tree until GUI verified.

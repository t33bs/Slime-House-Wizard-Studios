# Phase 15: occluded layer Move Original preflight

The destructive-move safety preflight now evaluates topmost contributing pixels first and subtracts those pixels before considering underlying layers. This matches the existing topmost-layer erase behavior, preventing an entirely occluded rotated/resized lower layer from rejecting an otherwise safe selection from an editable top layer.

No safety bypass was introduced for transformed or pose-local source buffers. Move Original remains the default; Copy Pixels remains available. This is a targeted source fix, not confirmation of the user's original Windows failure. Windows GUI verification is still required.

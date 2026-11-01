# Phase 14: transformed-layer guard behavior audit

The existing temporary Move Original safety guard was checked behaviorally, not only by inspecting source text. It allows untransformed artwork, blocks rotated layers, blocks resized layers, and ignores invisible transformed layers. This does not implement inverse-coordinate mapping: Move Original remains intentionally unavailable when visible transformed layers could make source erasure destructive. Windows visual checks remain deferred.

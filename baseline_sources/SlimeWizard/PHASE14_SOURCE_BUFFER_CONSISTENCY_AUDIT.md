# Phase 14 — Source buffer consistency audit

## Finding
The legacy Slimer erase path mutates both `parts[i]['image']` and `originals[i]`, while rendering may read a pose-specific `source_png`. Previously, the guard checked the rendered source against the editable part but not against `originals[i]`. A stale original could therefore pass the guard even though the operation was not editing the same image the renderer used.

## Change
The guard now compares size and RGBA bytes across all three sources: resolved rendered source, editable part image, and original backing buffer. Mismatches block destructive Move Original. The guarded transformed-layer path already checks the part against originals and rejects saved-pose sources.

## Verification
Two regression tests added. Full headless suite: 315 passed, 1 skipped, 441 subtests passed. Python compileall passed. Windows GUI visual verification remains deferred.

## Remaining work
Pose-local source editing needs explicit frame ownership and undo/redo integration. Multiple transformed layers and alpha compositing still require a safe source-erase policy. No Windows GUI test claimed.

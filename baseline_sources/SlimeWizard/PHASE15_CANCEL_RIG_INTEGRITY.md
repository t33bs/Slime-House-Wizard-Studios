# Phase 15 — provisional layer cancellation and rig integrity

- Cancellation of a newly appended, unconfirmed Slimer layer now uses a model operation that removes its image/source and associated rotation, anchor and attachment records together.
- Any other part that was attached to the cancelled layer is detached, avoiding dangling parent indices.
- Cancellation refuses to shift indices if another asset has been appended after the staged layer. The original artwork remains unchanged.
- Added three headless regression tests, including repeated creation at the same asset index and an invalid cancellation case.
- Tests: 398 passed, 11 skipped, 12 subtests passed. GUI tests skipped without PySide6; Windows verification remains outstanding.
- GitHub working tree not modified.

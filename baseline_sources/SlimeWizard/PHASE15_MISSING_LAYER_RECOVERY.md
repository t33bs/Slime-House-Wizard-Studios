# Phase 15: missing staged layer recovery

Apply Move now recognizes when an unconfirmed layer was deleted or removed by undo, and uses the existing safe cancellation routine to release its pending selection and mode lock. It does not erase original pixels or confirm an unrelated asset by stale index. This complements the existing cancellation recovery behavior.

Automated tests: 389 passed, 10 skipped, 12 subtests passed. GUI tests are skipped without PySide6. Consecutive Move Original, editing-table transforms, and save/reopen persistence remain Windows acceptance gates. Timeline reorder remains deferred.

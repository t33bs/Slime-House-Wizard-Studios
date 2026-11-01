# Phase 15 — invalid pending source snapshot guard

Apply Move now validates that a staged transaction has a source snapshot, a nonempty selection mask, matching canvas dimensions, and an explicit Move Original/Copy policy before it attempts to render or erase source pixels. An invalid transaction fails closed without changing artwork. A Windows Qt regression test covers a missing snapshot. This is a defensive fix, not proof that repeated Apply Move succeeds on Windows.

Headless: 405 passed, 16 skipped, 12 subtests passed. Windows GUI test remains skipped in this environment.

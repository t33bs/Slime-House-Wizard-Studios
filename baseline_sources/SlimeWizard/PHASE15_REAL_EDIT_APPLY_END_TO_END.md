# Phase 61 — Real Edit Selection → Apply Move regression coverage

New headless regression tests extract and execute the production UI methods with a minimal Qt-free harness, using the real PetSuiteModel and real Slimer source-mapping/erasure implementation.

Cases:
- Three consecutive Move Original Pixels transactions, including selecting from an earlier committed Slimer layer.
- Repeated Copy Pixels transactions retain the original artwork.
- A fully off-canvas destination rejects Apply Move without erasing source, then the same staged layer can be moved back and confirmed.

These tests cover the actual creation, pending transaction, validation, source erasure, selection reset, and confirmation methods, not just isolated source erasures. They are not a replacement for Windows GUI testing (PySide6 is not installed in the test environment).

Full test suite: 436 passed, 17 skipped, 12 subtests passed.

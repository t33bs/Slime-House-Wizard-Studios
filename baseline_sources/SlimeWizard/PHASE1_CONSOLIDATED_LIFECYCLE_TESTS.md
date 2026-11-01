# Phase 1 — Consolidated timeline lifecycle regression

Added `tests/test_phase1_consolidated_lifecycle.py`.

- Reorder three saved poses; compare each pose's rendered RGBA bytes against its original pose ID.
- Duplicate one pose, edit it, restore it, and confirm all other saved poses are pixel-identical.
- Exercise insert/copy/move/delete across four animations and verify global pose-ID uniqueness.

Test command: `python -m pytest -q`
Result: 208 passed, 433 subtests passed.

This is headless model testing. PySide6 is not installed in this environment; real Windows GUI mouse interactions, legacy duplicate-layer migration, and Windows EXE packaging remain unverified. Do not declare the pixel-loss issue fixed based solely on these tests.

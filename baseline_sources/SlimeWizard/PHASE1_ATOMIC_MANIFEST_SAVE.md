# Phase 1: safer project manifest saves

The JSON project manifest is written to a temporary file in the destination directory, flushed and synced, then atomically replaced with `os.replace`. Failed replacements preserve the previous JSON and clean temporary files. Regression test: `tests/test_phase1_atomic_manifest.py`.

**Scope limitation:** source PNG files are still saved directly; this change does not provide transaction-wide atomicity for asset PNGs and JSON together. Windows GUI save/reopen, interruption scenarios, and existing-project compatibility remain on the deferred verification list.

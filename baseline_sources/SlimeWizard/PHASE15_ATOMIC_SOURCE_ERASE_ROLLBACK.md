# Phase 15 — Atomic source-erase rollback

Move Original Pixels now snapshots source part images and originals before the destructive erase. If erasure raises an exception after partial mutation, both collections are restored and Apply Move fails without clearing the staged layer. Existing editing table and Copy Pixels behavior are unchanged.

Regression: tests/test_phase15_atomic_source_erase.py simulates partial modification of two buffers and verifies restoration. The standard headless suite passes; Windows Qt GUI tests remain skipped in this environment.

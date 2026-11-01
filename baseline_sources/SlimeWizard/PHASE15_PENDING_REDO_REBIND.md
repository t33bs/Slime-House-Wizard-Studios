# Phase 15 — Pending Slimer Redo Rebind

Redo of an undone provisional Edit Selection now attempts to rebind the pending transaction to the recreated layer. It verifies the layer remains last, its name matches, and the source beneath it still matches the captured pre-staging source. When verified, the original mask and Move Original/Copy policy are restored, and the policy checkbox is locked until Apply Move or Cancel.

An unrelated model edit invalidates the redo token. Unsafe or mismatched redo states are not rebound.

A new Qt GUI regression tests Edit Selection → Undo → Redo → Cancel. This GUI test is skipped without PySide6 and needs Windows verification.

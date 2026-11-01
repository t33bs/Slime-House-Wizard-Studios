# Phase 15: consecutive editing-table GUI gate

- Repaired a GUI test that imported nonexistent `FriendlyAnimator`; actual window class is `Suite`. This test had been skipped on headless Linux, masking the import failure on Windows.
- Added offscreen Qt regression for two consecutive Edit Selection -> move through existing X editing control -> Apply Move operations on one canvas, checking exact source/destination pixels, distinct real layers, and unchanged pose count.
- These GUI tests require PySide6 and are skipped in environments without it. No claim of Windows success until run there.
- No GitHub working tree modifications.

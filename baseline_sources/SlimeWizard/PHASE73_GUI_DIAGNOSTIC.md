# Phase 73 — Edit Selection button diagnostic

Starting point: reconstructed Phase 72 source.

Changes:
- Corrected Slimer activation status to direct users to Edit Selection instead of retired Finish Selecting.
- Added `tests/test_phase73_edit_selection_button_gui.py` exercising actual Edit Selection button click, staged Asset Library entry, Apply Move, and Move Original/Copy mode behavior.

Local validation: compilation passed; targeted tests 5 passed, 1 skipped. The GUI test is skipped because PySide6 is unavailable in this environment; it must be run in the user's existing Windows PySide6 6.12 virtual environment.

Run on Windows from project root:
`& "$env:USERPROFILE\Downloads\DocumentsSlime-Wizard-Pre-Merge-Backup\.venv\Scripts\python.exe" -m pytest -q tests/test_phase73_edit_selection_button_gui.py`

If GUI test fails, preserve full traceback and the app status after Edit Selection. Do not remove source-integrity safeguards to make staging pass.

No GitHub operations performed.

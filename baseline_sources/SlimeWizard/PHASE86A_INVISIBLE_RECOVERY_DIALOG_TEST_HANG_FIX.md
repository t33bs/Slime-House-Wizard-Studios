# Phase 86A — Prevent GUI pytest hang caused by invisible recovery prompt

## What happened

User Windows PowerShell: `pytest -vv -s tests/test_phase86_repeat_alpha_gui.py` collected 2 items but did not complete the first GUI test. Console displayed `QFontDatabase: Cannot find font directory ... PySide6/Qt/fonts` and two `This plugin does not support propagateSizeHints()` warnings. These warnings by themselves do not prove the root cause.

## Root cause targeted

`Suite.__init__()` always schedules `QTimer.singleShot(0, self.offer_recovery)`. The Phase86 test `make_window()` calls `w.show(); app.processEvents()`. If the real Windows user already has auto-recovery snapshots, `offer_recovery()` raises a modal `QMessageBox.question` **in Qt offscreen mode**. It is impossible to interact with the invisible modal; pytest appears frozen and Ctrl+C may fail while inside the native modal loop. This is a strong code-supported cause but is still pending confirmation by Windows rerun.

Even more important, `Suite.closeEvent()` deletes each project's recovery via `discard_project_recovery(project_id)`. Qt GUI tests must never alter a user's actual autosave backups.

## Fix

- Added `tests/conftest.py` with **opt-in** `isolate_gui_recovery` fixture. Only GUI modules that request it are affected. Does not change production `friendly_animator.py` or `studio/recovery.py`.
- The fixture patches the Suite's scheduled recovery prompt before construction, and disables recovery writes/deletes for the duration of each test. It does **not** remove or modify the user's snapshots.
- Applied fixture to Phase86, Phase85, Phase83, and Phase84 Windows GUI acceptance modules. Legacy recovery tests are unaffected.
- The Qt font path and propagateSizeHints output may still appear: these are warnings and not evidence of a test failure.

## Windows verification

Extract this zip into a new folder, launch PowerShell there, and run:

```powershell
& "$env:USERPROFILE\Downloads\DocumentsSlime-Wizard-Pre-Merge-Backup\.venv\Scripts\python.exe" -m pytest -vv -s tests/test_phase86_repeat_alpha_gui.py
```

Then run:

```powershell
& "$env:USERPROFILE\Downloads\DocumentsSlime-Wizard-Pre-Merge-Backup\.venv\Scripts\python.exe" -m pytest -q tests/test_phase86_repeat_alpha_gui.py tests/test_phase85_resize_and_selection_recovery_gui.py tests/test_phase83_repeat_source_focus_gui.py
```

App source functional changes are exactly Phase86; this is a test-harness-only hotfix. Production startup recovery is unchanged. GitHub untouched.

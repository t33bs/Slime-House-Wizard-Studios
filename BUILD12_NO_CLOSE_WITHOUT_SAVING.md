# SHWS Build 1.2 — No closes without saving

Base: Build 1.1 full source (`SHWS-Build1.1-Save-Creature-Draft-Fix-Full-Source.zip`), including the approved installer path correction and the unfinished-next-pose `.rig.json` save/reopen fix. Standalone Slime Buddy is untouched.

## Corrected SHS close prompt

The integrated SHS editor previously wrote an autosave recovery copy **before** asking whether to close, and treated **No** as “stay open.” That made it impossible to choose “No” to exit without preserving unsaved changes.

The SHS close confirmation now has explicit **Yes / No / Cancel** buttons, defaulting to Cancel:

- **Yes:** Write a recovery backup, then close, to offer restoration on next launch. Do not overwrite the last explicitly saved project.
- **No:** Discard the SHS recovery copy (including a previously scheduled autosave) and close. Do **not** save changes to the project JSON or create new recovery data.
- **Cancel:** Stay open. Do not modify project or recovery files.

If Yes cannot save the recovery, closing is blocked. If No cannot remove an old recovery file, closing is blocked and a warning is shown, rather than pretending unsaved material was discarded.

The Slime Wizard editor already provides **Save / Discard / Cancel**, where **Discard** closes without saving; it is intentionally unchanged. In the combined application the host still prompts each dirty editor independently.

## Verification

- Production change is limited to `studio/app.py` `MainWindow.closeEvent()`; all other SHS editor functions compare AST-identically against retained baselines.
- All Build 1.1 unfinished-next-pose saving behavior and project round-trip tests retained.
- Added seven Windows PySide6 GUI-path tests for No, Cancel, Yes, failed recovery, unexpected result, cleanup failure, and clean close.
- Added platform-independent close-contract tests.
- Windows GUI tests require PySide6 and must execute in Windows CI before shipping an EXE. Python-only tests cannot verify modal dialog rendering on the user's PC.

## Quick Windows acceptance

1. Open the integrated application, edit an SHS layer without saving, and click the application's X.
2. Click **Cancel**: app stays open, artwork remains.
3. Click the X again, choose **No**: app closes without writing the edited project. Reopening should not offer a recovery from the discarded SHS edits.
4. Repeat with **Yes**: close with recovery, relaunch, and choose to restore the work.
5. Make unsaved Slime Wizard pose edits and close the combined app: choose **Discard** on the Wizard prompt to exit without saving its creature. **Cancel** on either editor should prevent closing the combined app.

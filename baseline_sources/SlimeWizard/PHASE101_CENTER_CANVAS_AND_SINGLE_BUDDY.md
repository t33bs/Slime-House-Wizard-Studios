# Phase 101 — Center Canvas / Project Tabs Visuals + One Buddy Toggle

## Scope and baseline
Based on Phase 100 (visually approved by user; 10/10 targeted Windows GUI tests passed). The requested screenshot remains the target design. This build restyles **existing** center-editor surfaces, without adding tools, buttons, actions, shortcuts, workspace generation, or pose-editing behavior.

## Visual changes
- Existing main canvas container and heading: blue/navy framing, violet highlights, more cohesive section trim; native pixel rendering is unchanged.
- Existing canvas view row: same Fit to Canvas button and wheel/pan hint; better contrast and bordered zoom readout.
- Existing project tab strip: purple active tab / blue inactive tab; the existing + project button is restyled but not duplicated or rewired.
- The legacy canvas inline background/border changes color only; it retains the 380px minimum and all canvas events.
- The new Phase101 stylesheet stays in `studio/ui_pixel_theme.py`, additive to prior Phase99/100 themes.

## Requested duplicate removal
- Remove ONLY the redundant ON checkbox inside Buddy’s right-side Production Assistant header.
- Retain the existing **single top toolbar Slime Buddy ON/OFF checkbox** (`topSlimeBuddyToggle`) and its existing `refresh_buddy` and QSettings persistence connections.
- Buddy mascot and speech bubble still hide/show; the Production Assistant workspace and preview remain available.
- There are exactly two fewer `.toggled.connect(...)` sites because the removed checkbox had two cross-sync signals; all other connected sites are preserved.

## Evidence and limitations
- All 153 Suite non-constructor AST methods match Phase 100 exactly (hash manifest retained in `tests/phase101_phase100_method_hashes.json`). DragCanvas methods unchanged.
- Only Suite.__init__ changes within `friendly_animator.py`.
- Local full pytest: **514 passed, 49 skipped, 12 subtests**. Windows PySide6 GUI tests are skipped in this runtime; user Windows confirmation required.
- Original Phase 98 (working rollback), 99 and 100 builds remain untouched. No GitHub push.

## Windows targeted gate
From the extracted Phase101 folder in PowerShell:

```powershell
& "$env:USERPROFILE\Downloads\DocumentsSlime-Wizard-Pre-Merge-Backup\.venv\Scripts\python.exe" -m pytest -q tests/test_phase101_center_chrome_gui.py tests/test_phase100_left_panel_skin_gui.py tests/test_phase99_visual_skin_gui.py tests/test_phase98_real_gui_recovery_cleaner.py tests/test_phase97_collapsible_buddy_workspace_gui.py tests/test_phase96_place_frame_new_pose_gui.py tests/test_phase79_toolbar_buddy_gui.py
```

**Target: 14 passed.**

Then launch:

```powershell
& "$env:USERPROFILE\Downloads\DocumentsSlime-Wizard-Pre-Merge-Backup\.venv\Scripts\python.exe" .\friendly_animator.py
```

Visual check: only ONE Slime Buddy ON/OFF control in the top bar; verify it hides/reveals Buddy portrait and bubble. Inspect violet project tab and cyan view controls; Fit to Canvas works; zoom wheel / transform handles still visible; assets and timeline still reachable. Use a *copy* of the Swordcat project to check Place Frame, the Cleaner on Combined Artwork and save/reopen pose independence. If any functional change is seen, roll back to accepted Phase100 (for visuals) or Phase98 (fully verified workflow).

Next design-only Phase102: timeline frame thumbnails and existing timeline controls; no new tools/buttons.

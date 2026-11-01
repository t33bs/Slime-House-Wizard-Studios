# Slime Wizard Phase 99 — Visual Shell and Existing Button Skin

**Status:** candidate for Windows GUI/manual acceptance. Functional baseline: Phase 98.

## Approved scope

This phase implements the **first** part of the artist-approved dark navy/purple/cyan pixel-fantasy UI design. It does **not** add tools or functional buttons. All existing buttons retain their original callbacks, hotkeys, file formats, and editing semantics. Phase 98's separate pose draft/autosave fix and transformed/combined-artwork Cleaner behavior are retained.

### Implemented

- New decorative `Slime Wizard` header with the existing blue wizard-hat Slime Buddy portrait and subtitle.
- Consistent deep-navy panels, violet section headers/tabs and cyan emphasis.
- Existing QPushButtons/QToolButtons are restyled with beveled hover, pressed, selected, disabled, primary, success, and caution states. **No button was added for generation**, since Buddy's independent engine is not integrated.
- Restyled existing top toolbar, tool headings, selected tool state, status strip, asset/timeline borders, canvas border, production-assistant dock, preview collapse button, and scroll/splitter chrome.
- One previously too-literal heading test now accepts the reskinned timeline title while still requiring every actual timeline control.
- `studio/ui_pixel_theme.py` contains only QSS styling. The only existing Suite method changed is its widget-creation constructor (`__init__`); every other application method has the exact same AST as Phase 98.

### Explicitly *not* done

- The concept's depicted new Paint/Fill/Generate/Adapt/Analyze and other capabilities are **not** created as inactive or misleading buttons. They belong to later feature work (if approved), not this reskin.
- No editing algorithms, Slimer/Cleaner mechanics, layer visibility, Pose 1→2 creation, timeline actions, autosave or export behavior changed.
- No new button commands, changed shortcuts, or project-file schema changes.
- No live independent Buddy production engine yet; the existing disconnect notice stays accurate.
- This is not yet a pixel-perfect recreation of the illustrated concept. Phase 100+ will refine positions, iconography, space and sizing **without introducing new tools or behavior**.

## Verification completed (headless Linux)

- `python -m pytest -q`: **509 passed, 47 skipped, 12 subtests passed**.
- `python -m compileall -q friendly_animator.py studio tests`: passed.
- Phase 98 vs Phase 99: 154 Suite methods, only `__init__` altered; counts of Qt callback connections unchanged.
- No application implementation modules altered except the Suite constructor; added only `studio/ui_pixel_theme.py`.
- Windows PySide6 UI validation is **pending**; this environment does not provide PySide6.

## Windows test — extract the ZIP to a NEW folder

Open PowerShell in extracted Phase 99 folder and run:

```powershell
& "$env:USERPROFILE\Downloads\DocumentsSlime-Wizard-Pre-Merge-Backup\.venv\Scripts\python.exe" -m pytest -q tests/test_phase99_visual_skin_gui.py tests/test_phase98_real_gui_recovery_cleaner.py tests/test_phase97_collapsible_buddy_workspace_gui.py tests/test_phase96_place_frame_new_pose_gui.py
```

Expected: **9 passed**, zero failed (2 + 2 + 3 + 2).

Launch from the same folder:

```powershell
& "$env:USERPROFILE\Downloads\DocumentsSlime-Wizard-Pre-Merge-Backup\.venv\Scripts\python.exe" .\friendly_animator.py
```

### Visual/functional acceptance

1. Window opens with dark navy/violet shell, blue Buddy mascot, new headings and styled **existing** buttons.
2. Buttons are legible, do not clip on your monitor, and pressed/active/disabled states are visually distinguishable.
3. Animation Preview collapses/expands, resizing leaves Buddy visible, and Buddy ON/OFF works.
4. Start from original Swordcat PNG in a disposable project: Place Frame for untouched Pose 1, apply two leg movements, wait >60 seconds, Place Frame for Pose 2, and confirm Pose 1 remains unchanged.
5. Cleaner can erase on a Combined Artwork layer; save and reopen the poses and timeline order.

## Rollback

Revert by launching the separate Phase 98 ZIP. Do not modify or overwrite the previously verified Phase 96A backup. No GitHub operations performed.

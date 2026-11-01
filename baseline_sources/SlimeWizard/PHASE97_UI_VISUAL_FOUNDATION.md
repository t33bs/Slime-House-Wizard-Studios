# Phase 97 — Slime Wizard UI visual foundation (candidate)

## Scope: presentation only

This is a **separate Phase 97 candidate**, based on the verified **Phase 96A checkpoint**. It does not implement new artistic tools, modify editor actions, or connect Slime Buddy's independent generation engine. The Phase 96A Place Frame behavior remains intact: creating the next pose must not overwrite earlier saved poses.

### Visual upgrades
- Change the main window title to **Slime Wizard** and shift the existing Qt widget colors to a dark navy / cyan-pixel-workshop palette. All original toolbar actions, shortcuts, layer controls, the canvas, timeline, and exports remain present.
- Display the artist-provided **blue slime wizard with purple hat and wand** in the right-side Slime Buddy panel, using a 176×176 transparent pixel portrait with nearest-neighbor scaling.
- Give Buddy a dedicated **Production Assistant workspace** separate from the human editing UI. It states explicitly that his *own* independent engine is **not connected** in this build. There are no dummy generation buttons.
- Keep the real animation preview controls, existing live Slimer preview, clean frame preview, speed, loop and playback inside a **collapsible Animation Preview section**.
- Collapse only the animation preview content. This frees vertical space for Buddy while leaving the canvas, pose timeline, assets and tool palette untouched.
- The right-side vertical divider remains draggable. Save/restore the collapsed state and expanded divider proportions in QSettings, including recovery from a splitter reporting zero sizes before first show.
- Maintain the original top Slime Buddy ON/OFF switch and secondary Buddy panel toggle. OFF hides mascot/tip while human editing tools stay enabled.

### Not changed
- **No modifications** to `studio/*` production/model modules or Slimer / Cleaner / Place Frame / timeline / save / export methods. Only Qt presentation code and tests in `friendly_animator.py` were changed.
- No connection to Slime Buddy's standalone generation service. No automatic file overwrites or agent-driven editor actions.
- No reference-image viewer, comparison import, or deprecated recipe UI is restored. Real artwork imports stay.
- No GitHub push or release/installer action. Earlier ZIPs and projects are not modified.

### Acceptance tests
Run from extracted Phase 97 folder on Windows with the existing PySide6 virtual environment:

```powershell
& "$env:USERPROFILE\Downloads\DocumentsSlime-Wizard-Pre-Merge-Backup\.venv\Scripts\python.exe" -m pytest -q tests/test_phase97_collapsible_buddy_workspace_gui.py tests/test_phase96_place_frame_new_pose_gui.py tests/test_phase95_actual_gui_place_frame.py
```

Expected: **7 passed** (3 UI + 2 Phase96 + 2 Phase95) if Windows/Qt conditions are healthy.

Launch:

```powershell
& "$env:USERPROFILE\Downloads\DocumentsSlime-Wizard-Pre-Merge-Backup\.venv\Scripts\python.exe" .\friendly_animator.py
```

In the actual app: collapse/expand **Animation Preview** several times, confirm all preview controls return, toggle Buddy OFF/ON, drag the right divider, close/reopen and confirm layout, then use a disposable Swordcat project to check one Place Frame does not affect an earlier pose. Confirm frame playback, exports, import, and Slimer still work. Test with the window maximized and smaller if possible.

### Verification status
- Local headless Python regression suite: see packaged test report / handoff.
- PySide6 is not installed in the development container; Windows Qt tests and manual UI acceptance are **pending**.
- Phase 96A was already user-accepted: 15 Windows targeted tests passed; user manually verified that Place Frame no longer overwrites Pose 1.
- Slime Cleaner activation is working when the user cancels an unconfirmed layer first; no Cleaner changes made.

# Phase 96 — Place Frame records the NEXT pose, never the previous saved pose

## Exact manual report
Phase 95 Windows targeted tests: user confirmed **13 passed**, but when using their real Swordcat, they clicked Place Frame, applied two independent Slimer leg movements, then clicked Place Frame again. The two thumbnails appeared identical; an earlier pose seemed to have been overwritten. Their screenshot showed two poses and the old Phase95 status `Pose 2 created from pose 1; older 1 saved pose(s) verified unchanged`. This strongly suggests a **workflow/semantics defect** in addition to any possible UI state problems: Phase95's `slimer_place_frame` first called `preserve_pose_draft()`, intentionally writing the newly edited live canvas into the *selected previous pose*, then duplicated it as the next. The saved-pose integrity guard only captured snapshots AFTER that write, so it could report 'unchanged' despite the user's original pose having changed. The saved editable `.rig.json` project was not provided, so do not claim a separate unknown data-mutation bug was proved or ruled out.

## New behavior
- First `Place Frame` on an empty timeline captures the current base artwork as Pose 1.
- After two Slimer highlight -> Edit Selection -> Apply Move transactions, `Place Frame` captures the live result **as NEW Pose 2** while preserving Pose 1's exact old encoded source PNGs, original positions, visibility, pose ID, and rendered RGBA bytes.
- After editing again, `Place Frame` captures those edits **as NEW Pose 3** while preserving Poses 1 and 2 unchanged.
- If live artwork is unchanged, the next pose intentionally starts as an identical copy, ready for another edit.
- `Save Current Pose` remains the explicit user action to REPLACE an existing saved pose in-place. Its tooltip now explains this difference. `Place Frame` tooltip and post-Apply Move status explain that Place Frame saves as a new pose.
- Existing layer-and-source provenance, Move Original/Copy Pixels modes, user-chosen motion, ability to revisit saved poses, snapshot identity checks, GUI test-pose matching, old backups, no reference features, and all exports are retained.

## Technical correction
Removed the *executed* `self.preserve_pose_draft()` from `slimer_place_frame`. Instead, capture `old_frames` and IDs **before** any automatic saving; capture `source_pose = self.model.snapshot()` from the working canvas; insert that explicit source into the next timeline entry (or combine it into a *new* working layer for the new pose only). Phase95's full old-frame state + RGBA signature guard stays active. Switching to the new frame must clear stale draft ownership before loading the newly inserted pose.

## Tests
- New Windows GUI regression: `tests/test_phase96_place_frame_new_pose_gui.py`: real Place Frame, Edit Selection and Apply Move button clicks, two separate selected leg pixels, old frame fidelity, timeline round trip, project save/reopen, plus explicit Save Current Pose path.
- Previous Phase95/93/88/87 Windows GUI tests were adapted to assert **stronger distinctions between saved frames with the new save-as-next semantics**, not weakened to tolerate identical poses.
- Headless `tests/test_phase96_place_frame_snapshot_model.py` checks both individually moved pixels remain in the new combined sprite, original saved pose unchanged, and no executed `preserve_pose_draft()` in Place Frame.
- Local suite: 500 passed, 44 skipped, 12 subtests. PySide6 not installed here; Phase96 Windows GUI tests **NOT YET RUN**. Compileall passed. Package integrity tested.

## Windows targeted tests (expected 15 passed if all old 13 pass and new two pass)
From the new Phase96 extraction folder:

```powershell
& "$env:USERPROFILE\Downloads\DocumentsSlime-Wizard-Pre-Merge-Backup\.venv\Scripts\python.exe" -m pytest -q tests/test_phase96_place_frame_new_pose_gui.py tests/test_phase95_actual_gui_place_frame.py tests/test_phase94_edit_selection_active_gui.py tests/test_phase93_pose_identity_gui.py tests/test_phase91_no_reference_gui.py tests/test_phase88_first_place_frame_gui.py tests/test_phase87_pose_merge_gui.py tests/test_phase86_repeat_alpha_gui.py
```

## Manual test (use NEW blank project or copy of Swordcat; do not reuse an already-overwritten timeline)
1. Import an untouched Swordcat PNG. Click **Place Frame ONCE** to capture Pose 1 BEFORE touching the legs.
2. Highlight left leg, **Edit Selection**, move, **Apply Move**. Repeat for other leg.
3. Click **Place Frame** to record Pose 2; check Pose 1 and Pose 2 thumbnails differ and selecting Pose 1 displays original legs.
4. Edit again; click Place Frame to record Pose 3; check all three remain distinct where expected. Save creature; reopen; recheck.
5. If it still fails, collect ZIP of saved project `.rig.json` AND matching asset directory, with steps/screenshot of status text. Exported sprite sheet+JSON alone cannot reveal saved editable layers.

## Known outstanding
- Slime Cleaner intermittently fails to activate after Apply Move. **Not fixed in Phase96.**
- Returning to a saved pose and editing it, then switching poses or saving the entire creature *without first clicking Place Frame*, may still trigger the legacy automatic draft-save behavior. The specific reported Place Frame sequence is changed; broader navigation/save workflow consistency needs future validation.
- Windows GUI and real Swordcat manual acceptance pending. Do not call Phase96 final until confirmed.
- No GitHub push; no backups deleted or modified.

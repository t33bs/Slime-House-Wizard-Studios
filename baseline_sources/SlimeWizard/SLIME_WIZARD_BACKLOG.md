## Visual redesign phases (approved concept; layout/style only)

- Phase 99: shell, header, palette and bevels for EXISTING buttons (candidate; Windows pending).
- Phase 100: left tool and Asset Library panel rearrangement (existing controls only).
- Phase 101: center canvas, project tabs, zoom and editor control styling.
- Phase 102: timeline thumbnails and controls restyling, no changes to pose algorithms.
- Phase 103: Buddy production-workspace visual polish and responsive layout; generation engine stays independent/unconnected until separately authorized.

## Phase 97 (UI-only candidate, 2026-10-31)
- [x] Dark navy/cyan reskin and blue Slime Buddy portrait in the right-side production workspace.
- [x] Collapsible/re-expandable Animation Preview, resizable divider and persisted right-dock layout, while keeping playback/Slimer previews intact.
- [x] Display future independent Buddy production-engine status honestly: engine NOT connected; human editor tools remain separate.
- [ ] Windows GUI test + real-user layout approval before adopting UI version.
- [ ] Later AI integration is independent of the manual Slime Wizard tool engine; generated assets require explicit user approval/import.

## Phase 96A accepted foundation (2026-10-31)
- [x] 15/15 targeted Windows tests passed, real Swordcat Place Frame overwrite manually confirmed fixed.
- [x] Slime Cleaner activation works after canceling an unconfirmed layer; retain safeguards, consider a clearer explanation if blocked.
- [ ] Optional separate saved project close/reopen manual verification of pose fidelity.


## Phase 96 (2026-10-31) — Place Frame save-as-next workflow
- [x] Correct Place Frame: edited live canvas is committed to next pose, never auto-saved to previous. Existing saved pixel-source snapshots independently retained.
- [x] Add two-move real button GUI regression and headless source fidelity checks.
- [ ] Run Windows Phase96 targeted 15 GUI tests and manually verify untouched Pose 1 vs edited Pose 2 and Pose 3 on REAL Swordcat with save/reopen.
- [ ] Fix Slime Cleaner intermittent activation after Apply Move.

## Phase 94 status (Edit Selection visual cue)
- **Candidate:** Edit Selection button lights up whenever its X/Y/R/S handle-editing mode is active; turns off when editing ends. Windows GUI verification pending.
- **Release blocker remains:** Phase 93 stable pose identity guard needs manual Swordcat confirmation that Pose 2 never overwrites Pose 1 when creating Pose 3.
- **Open:** Slime Cleaner behavior still needs reproduction/fix. No reference-image UI is permitted.

## Phase 88 — From the first pose onward; Slime Cleaner investigation

- [x] Place Frame from an edited but as-yet-unsaved Slimer source now yields a combined editable Pose 1, not only Pose 2+.
- [x] Keep original per-layer source snapshots hidden and preserve project save/reopen and pose independence.
- [ ] Confirm first-frame workflow and previous-pose recall in Windows PySide6 and real Swordcat manual test.
- [ ] Diagnose Slime Cleaner: topmost-only erase, coordinate mapping for rotated/resized layers, possible lower layers showing through, undo and per-pose persistence. Determine user-observed symptom before destructive behavior changes.

# Phase 87 — New Slimer pose starts as one editable combined asset (2026-10-31)

- [x] **Real Windows milestone:** User confirmed Phase86A two consecutive Slimer moves work and generate proper independent layers on the same Swordcat pose.
- [x] Auto-combine visible artwork into one new `Combined Artwork` layer when explicitly creating the NEXT pose from a Slimer-authored pose; prior pose's layers remain untouched.
- [x] Only show active new-pose layers in Asset Library (hide, never delete, older pose layers); reset Slimer so new combined base can be highlighted and edited again.
- [x] Preserve conventional multi-layer rigging workflows when Slimer was not used; no automatic frame creation on Apply Move.
- [x] Add headless and Windows GUI regression tests, source-PNG save/reload, undo/redo.
- [ ] Windows: run Phase87 merge tests and confirm pass count.
- [ ] Real Swordcat: edit two legs on Pose 1; place Pose 2; verify ONE active asset; highlight, edit, Apply Move again; return to Pose1 and check both original layers; save/reopen; verify alpha and pose thumbnails.

# Phase 86 — Second Slimer selection on real Swordcat (2026-10-30/31)

- [x] Root cause found: selected translucent alpha was falsely marked unmapped due to binary selection-vs-raw-alpha comparison.
- [x] Allow Move Original for independently sourced partially transparent pixels only when no lower-layer artwork contributes and provenance is complete.
- [x] Preserve strict multi-layer/composited and partial-scaled-source rejection; keep source unchanged on failure.
- [x] Add concise rejection counts for visibility and overlap, plus new headless and Windows tests.
- [ ] Run Phase 86 Windows GUI tests and report the pass/fail count.
- [ ] Real Swordcat: apply FIRST move/resize, then highlight a different area on the SAME pose, stage SECOND new layer, move and Apply Move, no reset or extra frame.
- [ ] If rejected, send exact `selected/translucent/multi-layer` status and screenshot for targeted follow-up; avoid assuming every refusal is due to translucent artwork.

# Phase 82 — Slimer repeat/edit lifecycle and Asset Library SHS export (2026-10-30)

- [x] Phase 81 milestone: user confirmed 7 Windows PySide6 tests passed and real Swordcat overlapping Move Original succeeded, with original selected pixels cleared and destination intact.
- [x] Phase 82: Edit Selection opens imported/previously confirmed Asset Library layer placement directly when highlight is empty; painted selections still create new independent move layers.
- [x] Phase 82: `Apply Move` for an existing layer confirms placement, hides handles, restores highlighter without adding animation frames.
- [x] Phase 82: rebase empty new highlight from current rendered artwork so subsequent selection is not stuck on stale source snapshot.
- [x] Phase 82: `Export for SHS` writes visible selected-layer pixel content with transparent PNG fidelity; trims mostly blank full-canvas Slimer source and bakes transformed layer; validates file after saving; status reports size/location.
- [ ] **Windows PySide6:** run Phase 82 repeat-placement and SHS export GUI tests. See `PHASE82_REPEAT_PLACEMENT_AND_SHS_EXPORT.md`.
- [ ] **Real Swordcat:** perform two consecutive highlighter -> Edit Selection -> Apply Move cycles with Move Original ON, no extra frame, handles OFF between cycles.
- [ ] **Real SHS export:** select an existing Slimer Layer and export its PNG, open in SHS/Paint to confirm visible pixels and transparency; verify PNG status/path and size.
- [ ] Decide whether a later version should auto-launch SHS after export. This release saves a PNG file only.

# Phase 81: Apply Move and Asset Library usability — 2026-10-30

- [x] Source erase excludes the pending destination during both preflight **and** actual erase; overlapping move regression is now covered.
- [x] Add visible Asset Library Import Asset / Export for SHS (lossless PNG source); preserve direct top-level import and no live SHS sync.
- [x] Show useful empty-highlight instruction rather than switching unrelated handles; refresh highlight snapshot after importing new artwork.
- [ ] **Windows PySide6:** run Phase 81 GUI gates (I/O, overlapping move, previous clean-preview tests).
- [ ] **Real Swordcat leg:** repeat the exact move that previously failed, including X/Y/R transform and Move Original ON at Apply Move; preserve any failure screenshot and newly detailed status.
- [ ] Check Copy Pixels, Cancel, undo/redo and project save/reopen after a real multi-layer move.

# Phase 80 clean-preview regression follow-up (2026-10-30)

- [x] Diagnose Phase 79 Windows PySide6 failure: 3 passed, 1 failed, green selected-pixel overlay contaminating clean Slimer Preview.
- [x] Fix PIL image aliasing in `refresh()` without changing editor canvas overlay rendering or source artwork.
- [ ] Windows: rerun Phase 78 + 79 + 80 GUI gates and confirm all pass.
- [ ] Manual: Slimer Preview displays clean Swordcat artwork during active highlights, Move Original staging, and joint guides, with no green tint or handles.

# Slime Wizard Development Backlog

Updated: 2026-10-30 — Phase 79 source package

## Phase 79: Remove duplicate canvas-top controls

- [x] Remove the old Slime Buddy station/recipe dropdown and the user-facing Check animation readiness row above canvas; no replacement menu or buttons.
- [x] Move the persistent Slime Buddy ON/OFF switch next to Easy Mode / Undo / Redo in the top toolbar; comparison-dock toggle stays synchronized.
- [x] Keep Import PNG assets, timeline, posing, saving/export and technical validation logic unchanged while recovering vertical canvas space.
- [ ] Run Phase 79 Windows PySide6 tests (`tests/test_phase79_toolbar_buddy_gui.py`) and visually verify actual new canvas height on Swordcat project, including with Buddy OFF.

## Phase 78: Zoom-friendly Slimer controls and clean preview

- [ ] Run `tests/test_phase78_zoom_handle_and_clean_preview_gui.py` on Windows with PySide6 6.12; drag X/Y/R handles with zoom centered on an edge-of-screen selected limb.
- [ ] Real Swordcat leg test: at small and large zoom, the selected handle remains on screen, can be clicked, and stays outside the floating Transform menu.
- [ ] Slimer Preview shows the full **current canvas artwork** (including the staged layer) without highlight color, bounding outline, X/Y/R controls, onion ghosts, or joint guides; Frame Preview continues its existing pose/timeline behavior.
- [ ] Confirm staged Move Original waits until Apply Move; Cancel preserves source; Copy Pixels remains available.

## Current gate — Windows PySide6 + real artwork testing

- [ ] Phase 77: collapsible **on-canvas** Transform handles menu (collapsed by default) shows correct active layer and exactly one X/Y/R handle; no new sidebar menu.
- [ ] Phase 77: switching handle modes changes visible/hit-tested handle but never commits, deletes, or duplicates pixels; Edit Selection toggles handles independently.
- [ ] Phase 77: on-canvas layer picker stays synchronized with the Asset Library and cannot change source layer mid-pending operation; allows switches after Apply/Cancel.

- [ ] Phase 76: X horizontal, Y vertical, R rotation handles are **visually present** near the selected art (including full-canvas transparent Slimer layers).
- [ ] Phase 76: Edit Selection shows/hides handles without creating another layer; chosen Asset Library row and label agree.
- [ ] Phase 76: User can select a different Asset Library layer **after Apply Move / Cancel**, not mid-pending destructive move.
- [ ] Phase 76: Test actual mouse rotation, degree input, repeated moves, Copy Pixels, Move Original Pixels ON by default, off-canvas safety and Undo/Redo.
- [ ] Previously reported selection-to-asset-layer failure: confirm against the user's real Swordcat source even if synthetic GUI tests pass.
- [ ] Windows font scaling, window layout, ghosting, tooltips, saving/reopening, frame and export verification.

## Post-critical-testing product work

- [ ] Asset Library Import Asset (transparent PNG, pixel-perfect) and Export to Slime House Studios (SHS), **export-only integration** to SHS for now. Decide direct launch vs save-to-folder when implementing.
- [ ] UI cleanup/reorganization, more usable canvas space, clear panel labels, beginner-friendly navigation, preserve existing working controls.
- [ ] Slime Buddy persistent ON/OFF, context-sensitive technical guidance, never prescriptive or judgmental about visual design.
- [ ] Slimer selection/color/layer workflow polish, no Finish Selecting button, one-button Edit Selection creation/edit; preservation of source-pixel and pose integrity.
- [ ] Reference Viewer PNG/GIF/APNG/sprite sheet zoom/preview and onion skin controls.
- [ ] Reliable animation pose/frame operations, previews, PNG frame/sprite sheet + JSON primary exports, GIF/APNG secondary preview exports.
- [ ] Windows installer/portable release and full novice walkthrough validation.

## Hard requirements

- Move Original Pixels is checked by default; Copy Pixels remains available. Clear selected original pixels **only after successful Apply Move**.
- Do not add frames while editing layers. Layers and saved poses remain independent. Never silently erase unselected pixels or overwrite previous poses.
- GitHub backup is protected: no commit/push/force-push without explicit authorization and verification.
- Each phase ships a complete, intact source ZIP and a regression-check note; preserve all old tests.

This is a working backlog, not a guarantee every historical feature is unimplemented. Reconcile with real code and future user decisions.

## Phase 83 checkpoint (2026-10-30)
- After Apply Move, restore previously selected source Asset Library row and hide handles; highlight immediately again on same pose.
- Highlight phase no longer draws a misleading dashed transform rectangle.
- Unsafe partial-alpha/occluded source selections remain blocked for Move Original; give recovery instructions (Clear Selection + edit existing layer, or Copy Pixels).
- Windows two-cycle GUI tests + real Swordcat confirmation still pending.

## Phase 84 checkpoint (2026-10-30)
- [x] Identify and hide the **yellow joint/pivot dot** left on the canvas by auto-created Slimer Layer anchors when editing is finished. This is distinct from the green highlight rectangle; do not confuse the two again.
- [ ] Windows PySide6 test: auto joint dot not visible outside Place a joint dot; pivot remains available for rotation.
- [ ] Windows hands-on: verify yellow dot vanishes after Apply Move on Swordcat and toggles during explicit joint-placement mode.
- [ ] Continue investigating second highlight Move Original rejection on real artwork (possibly translucent/overlapping pixels); safety guards remain intact.

## Phase 85 checkpoint — resize existing assets and second-selection safety (2026-10-30)
- [x] New **S / Resize** handle mode on canvas (no extra sidebar buttons), existing `Slime size %` now applies to selected editable layer.
- [x] Content-centered, nearest-neighbor Slimer resizing without stretching full-canvas transparent padding or silently clipping pixels.
- [x] Phase 84 manual yellow dot cleanup verified by user (no marker after Apply Move).
- [ ] Windows PySide6 tests for Phase 85 resize and recovery; then manually resize Slimer leg and imported asset.
- [ ] Continue investigating translucent/overlapping source provenance if user needs safe partial-alpha Move Original. Do NOT bypass source-erase safety or silently drop highlighted translucent pixels.
- [ ] Recheck two distinct *opaque* highlights in one pose after Apply Move, without a frame.

### Phase 89 — imported pose drag-reorder regression (local tests pass, Windows manual pending)
- `PoseTimelineList` suppresses premature row selection while dragging.
- Model reorder is deferred until Qt finishes drop, preserves both pose snapshots/IDs/timings and undo history.
- Windows test `tests/test_phase89_timeline_drag_import_gui.py`; hands-on drag after importing Pose PNG remains acceptance gate.
- Separate open issue: Slime Cleaner on transformed/overlapping layers; do not silently alter destructive erase behavior.
- Import Pose PNG now resets the already-preserved old pose's draft identity before loading new PNG, preventing back-save contamination.

### Phase 90 — Import pose PNG / alpha fidelity (2026-10-31)
- [x] Two explicit import choices: exact independent PNG (default) and composited over previous saved pose (dropdown).
- [x] Preserve black RGB/alpha exactly from source PNG; verify independent saved pose snapshots and avoid borrowed opaque pixels.
- [x] Hide inactive inherited Asset Library rows by default in selected pose, with Show inactive for inspection, not a change to other poses.
- [x] Model RGBA/snapshot/save-reopen/reorder tests; Windows GUI tests added.
- [ ] Run new GUI tests on user's Windows machine and manually compare actual Swordcat_Walk_Pose_1_128.png in both modes. The actual PNG was not available in this environment.
- [ ] Diagnose Slime Cleaner on actual user example (transformed vs overlapping vs ordinary), then implement a *separate* safe eraser fix with undo and pose isolation.

### Phase 91 — remove all visual reference content (2026-10-31)
- [x] Remove external image reference viewer, upload/reference buttons, frame stepping, independent reference playback, and unused reference parser.
- [x] Retain Slimer Preview, saved-pose preview, timeline thumbnails, GIF/APNG/sprite export, and real creature/Asset Library PNG imports.
- [x] Rename visible right pane and visibility actions to Preview, not Compare.
- [x] Change Slime Buddy Preview guidance to teach playback of the user's own poses, without recommending references.
- [x] Simplify internal preview clock to frame-only calculation without separate reference-frame synchronization.
- [x] Correct Phase 88 GUI test's empty-animation KeyError (test used direct dictionary indexing before first Place Frame).
- [x] Local regression: 495 passed, 40 skipped, 12 subtests passed (GUI still pending on Windows).
- [ ] Windows GUI checks: `tests/test_phase91_no_reference_gui.py`, `tests/test_phase88_first_place_frame_gui.py`, `tests/test_phase86_repeat_alpha_gui.py`.
- [ ] Manual verification that Pose 1 through later poses remain editable, hidden historical layers remain recoverable, and Slimer Preview/animation preview show current creature only.
- [ ] Slime Cleaner still has a separately reported malfunction. Gather a precise on-canvas example and implement its own fix; do not change erasure semantics during UI cleanup.
- [ ] Keep all older ZIPs and GitHub untouched until explicitly authorized.

### Phase 92 — previous pose remains layered on Place Frame (2026-10-31)
- [x] Remove prior-pose-flattening branch from `slimer_place_frame`; preserve saved pose Slimer layers and combine **new pose only**.
- [x] Fix stale Phase 88 GUI assertion: after Move Original +3, alpha 0 at old coordinate, 138 at destination. Assert prior Pose 1 layer visibility and next pose's single combined asset.
- [x] Add model RGBA + save/reopen independence regression; local tests green.
- [ ] Windows PySide6 gate: run Phase 91, 88, 87, 86 targeted GUI modules.
- [ ] Manually place Pose 1 and Pose 2, change separate Slimer layers, switch back, confirm old pose retains all its edits.
- [ ] Slime Cleaner: separately investigate incorrect erase behavior on overlapping or rotated assets; do not change pixels destructively without reproducing.

### Phase 93 — Cross-pose overwrite blocker (2026-10-31)
- [x] Save user report: Phase92 Windows 6 passed, **manual failure**: placing subsequent frame after editing Pose2 made Pose1 display same artwork.
- [x] Add stable ID-bound draft ownership, deny saves when live canvas belongs to different saved pose, resolve shifted row by pose ID.
- [x] Gate Place Frame / Save / Insert / Duplicate / Copy and per-pose visibility on live pose ownership; never overwrite other pose when UI selection is stale.
- [x] Add three **visibly distinct** pose regression plus intentional stale UI selection guard (Windows) and saved RGBA/pose ID roundtrip (headless).
- [x] Local non-GUI suite 497 passed, 41 skipped, 12 subtests passed.
- [ ] **Windows** run Phase93 targeted regression; real Swordcat manual check after editing Pose2 and placing Pose3, revisit Pose1 and Pose2, and save/reopen. Mark accepted only after visual confirmation.
- [ ] Slime Cleaner malfunction remains separate; no destructive changes in Phase93.
- [ ] No external reference viewer/upload features; retain actual artwork imports. No GitHub changes.

## Phase 95 — continuing overwrite report (blocking)
- [x] Guard Place Frame with real previous-frame pose-state and rendered-pixel comparison; abort/restore if old saved frame changes during insertion.
- [x] Confirm Qt-selected timeline row matches live canvas before Place Frame.
- [x] Add click-driven Qt test for real Place Frame/Edit Selection/Apply Move/timeline navigation/save-reopen; add 256x256 model test and read-only pose inspector.
- [ ] Windows: run Phase95 targeted Qt tests, looking for 13 passed.
- [ ] Real Swordcat: reproduce the manual overwritten Pose 1 symptom. If it persists, collect saved `.rig.json` and matching project assets folder or run inspector. Automated passes alone do NOT resolve the issue.
- [ ] Slime Cleaner malfunction remains open. GitHub untouched.

### Phase 102 — Timeline-only visual redesign (candidate)
- [x] Style existing frame thumbnails, duration, Save/Restore, Previous/Next, Insert/Import/Copy/Remove/Shift buttons to match approved concept.
- [x] Leave timeline reorder, Place Frame, autosave, Slimer, Cleaner, shortcuts and formats unchanged; assert method fingerprints, signal counts and no new Qt widgets.
- [x] Headless 518 passed / 50 skipped, 12 subtests.
- [ ] Windows: run `tests/test_phase102_timeline_skin_gui.py` with Phase101–96 and phase79 GUI regression modules; expect 15 passes.
- [ ] Visual/manual: verify thumbnails and selection are clear; timeline reorder in both directions and save/reopen with copy of Swordcat project.
- [ ] Next Phase103: Buddy right panel and preview visual consistency only; do not create AI controls or integrate production engine.

- [x] Phase103 final planned cosmetic pass: right dock, existing Buddy and preview widgets. Windows visual/test approval pending. No AI production engine integration.

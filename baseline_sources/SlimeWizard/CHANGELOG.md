## Phase 103 — Right Dock / Slime Buddy Visual Polish (2026-10-31)

- Design-only reskin of existing Slime Buddy workspace and collapsible Animation Preview, their labels, preview controls and right-panel border/spacing.
- No new tools/buttons/actions and no modifications to non-constructor methods, signals, pose data or editor functions. Blue mascot and single top Buddy toggle retained.
- 522 local tests passed, 51 skipped; Windows GUI validation pending.

## Phase 102 — Timeline Visual Redesign (candidate; Windows acceptance pending)

- Retro navy/purple/cyan/gold styling for existing timeline header, pose thumbnail list, frame duration, and all existing timeline action buttons. No new controls or actions.
- Freeze 153 existing non-constructor methods against Phase101 and verify 73 signal connections and widget constructor counts unchanged.
- Local full pytest: 518 passed, 50 skipped, 12 subtests; Windows GUI and visual review pending. Phase98 accepted rollback and prior ZIPs untouched.

## Phase 99 — Visual Shell and Existing Button Skin (candidate; Windows acceptance pending)

- Began user-approved pixel-fantasy navy/purple/cyan reskin by adding a decorative header, cohesive section/tab styling, and beveled states for EXISTING buttons. No tools, extra functional buttons, editing methods, project formats, or callbacks changed.
- Added `studio/ui_pixel_theme.py` for pure QSS styling and tests locking all non-constructor application methods and signal counts to Phase 98.
- Full headless suite: 509 passed, 47 skipped, 12 subtests passed. Windows verification pending; Phase 98 rollback preserved.

## Phase 98 — Prevent recovery autosave overwriting earlier pose; erase combined layers

- Separate unplaced Slimer/Slime Cleaner edits for next pose from explicit Save Current Pose. The 60-second recovery tick no longer saves those pending edits over a previous frame.
- Slime Cleaner now targets any topmost visible editable layer, including combined and rotated artwork, preserving lower/hidden and earlier-pose pixels.
- Preserve the Phase 97 Slime Buddy layout and collapsible animation preview. Full local regression: 505 passed, 46 skipped. Windows testing pending.

## Phase 97: Visual UI foundation / collapsible Buddy workspace (candidate)
- Switch to a dark navy/cyan desktop theme and the user-approved blue wizard slime portrait.
- Add Buddy's dedicated *independent* Production Assistant workspace (engine explicitly not connected in this UI-only build).
- Add collapsible Animation Preview with unchanged Slimer/live frame previews, playback controls, resize handle, and persisted layout preferences.
- No changes to human drawing/editing tools, Place Frame semantics, model, projects, or exports.
- Run Windows GUI acceptance and confirm the prior Phase 96A pose workflow is still sound before accepting.


## Phase 96: Place Frame creates the NEW edited pose without changing the previously saved pose
- Removed pre-insert autosave of the selected pose from Place Frame. The live canvas is now recorded as the next pose; the earlier saved snapshot stays unchanged.
- Distinguish Place Frame from explicit Save Current Pose; clarify UI tooltips and post-Apply Move status.
- Add actual-button two-leg GUI regression and independent model source-pixel tests; update pose tests for corrected semantics.
- Local 500 passed, 44 skipped; Windows GUI and real art still pending.

## Phase 95 — Pose frame overwrite guard and real-click diagnostics (candidate; not manually verified)
- After every Place Frame, compare all prior saved pose states, IDs and rendered RGBA pixels. Reject the new frame and restore prior snapshots if any older pose changes.
- Reject Place Frame if the selected Qt timeline row differs from the active editor frame.
- Improve status messaging so users know a newly created pose initially looks identical to its source and when previous poses were verified unchanged.
- Add clicked-button/Qt timeline/save-reopen Windows regression, 256x256 model test, and read-only pose inspector.
- **Manual user report remains unresolved until Windows and real Swordcat testing.**

## Phase 94 — Edit Selection active cue (2026-10-31)

- Highlight **Edit Selection** with vivid green fill/border and bold label when real transform handles are active; revert to normal when disabled, applied or cancelled.
- Display state follows the actual canvas edit state; a rejected click never appears active. One-button Slimer editing, image pixels, pose behavior and asset layers are unchanged.
- New Windows regression verifies stage/toggle/apply, edit existing layer, and rejected click; see `PHASE94_EDIT_SELECTION_ACTIVE_CUE.md`.
- Local tests: 497 passed, 42 skipped, 12 subtests passed; GUI tests pending on Windows.

## Phase 88 — Continuous Slimer combined source from Pose 1 (2026-10-31)

- First Place Frame now produces a single editable Combined Artwork source even when it is the first saved pose, provided Slimer moves already exist. Previously this required a saved earlier pose.
- The underlying original and Slimer layers remain preserved hidden in that new pose snapshot. All future poses continue the same workflow. Existing saved poses remain independent.
- No automatic flattening of ordinary rig layers; no frame creation by Apply Move; Move Original and Copy Pixels unchanged.
- Add headless, project round-trip and Windows PySide6 GUI tests. Cleaner remains a separately tracked bug pending precise symptom; existing pixel erasure semantics unchanged.
- See `PHASE88_FIRST_POSE_CONTINUOUS_WORKFLOW.md`.

## Phase 87 — Automatic one-layer working copy when creating a new Slimer pose (2026-10-31)

- User confirmed real Phase86A Swordcat can perform two consecutive Move Original edits, creating proper separate layers on one pose.
- Creating the next pose from a Slimer-edited pose now starts the **new** pose with a single Combined Artwork asset; previous pose layers stay independently editable and untouched.
- The new pose Asset Library shows only active layers; inherited originals are hidden, never deleted. Fresh Slimer highlighting, nearest-neighbor resizing and Move Original work on the new combined base.
- Copy/duplicate/insert also merge Slimer-authored poses. Ordinary non-Slimer rigging poses preserve their separate layer architecture.
- Added model save/reopen, source-RGBA preservation, undo/redo, and Windows GUI regression gates. See `PHASE87_AUTOMATIC_COMBINED_POSE.md`.

## Phase 86 — Repeat Slimer selection and exact alpha-presence provenance (2026-10-30)

- Fix false source-erase rejection: binary selection masks must be checked against binary alpha presence, not fractional alpha magnitude.
- Allow safe isolated translucent source pixels to move with exact RGBA intact; **still reject blending across layers** or incomplete scaled-source footprints.
- Add failure diagnostics (selected/translucent/multi-layer counts), repeat-selection and real multi-layer safety tests, and updated Windows PySide6 gates.
- Preserve Phase 85 resize/Apply Move, default Move Original, Copy Pixels, one-button Edit Selection, no new frames, joint guide visibility, and asset import/export.
- See `PHASE86_REPEAT_SELECTION_ALPHA_PROVENANCE_FIX.md`.

## Phase 85 — Resize handle and safe selection recovery (2026-10-30)

- Add **S — Resize artwork** to the collapsible on-canvas handle picker, one visible handle at a time.
- Connect the existing Slime size % control to the real selected asset; Slimer selection layers resize visible content about the pivot, not their transparent full-canvas padding.
- Preserve nearest-neighbor pixels, alpha, staged source safety, no-frame placement, and strict no-clipping checks; add GUI and headless regressions.
- Confirm Phase 84 yellow joint-dot cleanup via the user's screenshot; retain unsafe translucent/overlap Move Original rejection with explicit recovery path.
- See `PHASE85_RESIZE_HANDLE_AND_SAFE_SOURCE_RECOVERY.md`.

## Phase 84 — Hide lingering yellow joint guides outside placement mode (2026-10-30)

- Correct misdiagnosis of leftover "handle" on the leg: it was an auto-stored **yellow joint dot** in the canvas editor overlay, not the green highlight boundary. Neither preview showed it because only the canvas draws joint guides.
- Draw joint dots only when the explicit **Place a joint dot** tool is on, and redraw immediately on toggle; retain every saved rotation pivot and all pixel art unchanged.
- Phase 84 GUI tests cover immediate guide visibility and cleanup after Apply Move. Details: `PHASE84_EDITOR_JOINT_GUIDE_VISIBILITY.md`.
- Qt-free suite: 481 passed, 33 skipped, 12 subtests passed; Windows PySide6 GUI tests pending.

## Phase 82 — Consecutive Slimer and working SHS PNG export (2026-10-30)

- Simplified `Edit Selection` button can now open existing Asset Library layers for direct placement, with no duplicate layer or frame.
- Confirming existing layer placement hides transform handles and restores Slimer highlighting; new empty highlight rebases safely after previous edit.
- Export for SHS now uses the actual selected asset artwork and transforms. Full-canvas Slimer selections export tightly cropped pixels, not a mostly empty canvas. Untransformed small source PNGs keep original dimensions.
- Export validates real nontransparent RGBA pixels in the completed PNG and safely replaces destination only after success; status reports location and dimensions.
- Qt-free suite: 480 passed, 31 skipped, 12 subtests passed; Windows GUI tests pending.

## Phase 81 — Source erase staging fix and Asset Library I/O (2026-10-30)

- Exclude the provisional Slimer destination during **actual source erase**, matching the already-safe preflight; preserve original-pixel rollback and Move Original default ON.
- Fix overlapping selected-pixel moves accidentally consuming/erasing their own destination asset.
- Add Import Asset and Export for SHS to the Asset Library; save selected source RGBA PNG losslessly, no automatic SHS launch.
- Block Asset Library Import/Export while a Move Original/Copy layer is staged; refresh an old Slimer selection when importing new artwork.
- If no pixels are highlighted in Slimer paint mode, Edit Selection explains what is missing rather than silently toggling a different layer.
- Retain one-button Highlight → Edit Selection → Transform → Apply Move, Copy Pixels, source integrity, timeline isolation, and existing Windows test gates.
- Details: `PHASE81_SLIMER_APPLY_ASSET_LIBRARY.md`.

## Phase 80 — Clean Slimer Preview overlay isolation (2026-10-30)

- Fix green highlight contamination of Slimer Preview caused by PIL image aliasing between live render and editor-composite render in `refresh()`.
- Copy the editor buffer on first overlay mutation only; avoid copying on every no-overlay refresh.
- Regression tests for selected highlights and joint guides on Windows PySide6; leave Phase 79 layout intact and Move Original/Copy semantics unchanged.

## Phase 79 — Remove redundant station/readiness rows (2026-10-30)

- Removed the old Slime Buddy **Import / Assembly / Rigging / Poses / Timeline / Compare / Save / Export** station dropdown entirely from above the canvas.
- Removed the user-facing **Check animation readiness** row. The internal technical-check function and export validations are preserved for compatibility; the empty vertical UI strip is gone.
- Moved the persistent **Slime Buddy ON / OFF** switch to the upper Easy Mode / Undo / Redo toolbar; the comparison-dock ON toggle remains synchronized with it.
- Kept helpful, optional, nonjudgmental Slime Buddy guidance in the existing preview-dock speech bubble; it now selects context from active tool/artwork without a station dropdown.
- No change to canvas artwork, Slimer source erase timing, transform handles, timeline, project storage, exports or SHS integration.
- Added `tests/test_phase79_canvas_space_contract.py` (headless UI source regression) and `tests/test_phase79_toolbar_buddy_gui.py` (real PySide6 Windows layout + preference synchronization gate).
- Available suite: **469 passed, 26 skipped, 12 subtests passed**; GUI test requires Windows PySide6 6.12; compilation and ZIP integrity verified.

## Phase 77 — Collapsible on-canvas transform handles (2026-10-30)

- Added compact **Transform handles** popup on the canvas, collapsed by default; layer chooser and one-of X/Y/Rotate picker live there, not in the left panel.
- Only one selected handle is rendered and hit-testable at a time, and the chosen mode is reflected in the selected-layer label.
- Canvas layer picker mirrors the Asset Library selection; editing a staged Move Original/Copy layer locks layer switching until Apply Move or Cancel.
- Preserved one-button Edit Selection, default Move Original, Copy Pixels, source-pixel safety, animation frame integrity, and existing degree-input controls.
- Added Phase 77 PySide6 GUI tests; updated Phase 76 GUI and Qt-free handle math tests for intentional single-handle UI.

# Phase 75 — staged Slimer layer rotation (Windows validation pending)

- Fix rotation pivot and handle location for full-canvas transparent selection assets. Rotation is centered on the visible selection rather than the canvas.
- Existing `Slime rotate °` field now controls the staged editable Asset Library layer, synchronized with the Asset Library's `Turn part (degrees)` field and the blue mouse handle. Alt+drag on the staged artwork also rotates it.
- Preserve one-button Highlight → Edit Selection → Transform → Apply Move workflow and Move Original Pixels default ON; erase source only during a successful Apply Move.
- Add targeted GUI and headless regression coverage; Windows PySide6 GUI verification required before acceptance.

## v0.47.0 — Windows GUI smoke-test hardening

The packaged GUI smoke test now checks actual minimize/maximize states, restore-to-normal, and resize behavior against available screen geometry at 800×600, 1280×720 and 1920×1080 targets (clamped to runner screen). Windows CI logs Qt and OS diagnostics. These tests require execution on a Windows runner; they have not been executed in this environment.

## v0.46.0 — Windows installer upgrade regression

Added a Windows CI install/reinstall/uninstall lifecycle test. It runs packaged GUI smoke checks after both installs and compares the exact bytes of a user-project sentinel outside the installation directory before and after each operation. This is a same-version reinstall rehearsal, not yet a true cross-version upgrade test. Windows workflow has not executed here.

## v0.45.0 — Windows installer lifecycle validation
- GitHub Actions now runs a real silent installation, starts the **installed** EXE in GUI smoke-test mode, invokes the actual uninstaller, and checks the installed EXE was removed.
- Captures installer log as a failure artifact when available.
- Adds two pipeline regression tests.
- Windows CI has not yet been executed here: this is an unverified Windows test workflow, not a passed installer run.

## v0.44.0 — Phase 5 Windows packaging smoke-test checkpoint
- Added `--smoke-test` to exercise the real PySide6 application startup, minimize/maximize/restore transitions, and offline Slime Buddy/template resources.
- Windows GitHub Actions now executes the **packaged EXE** smoke test and fails the build if it exits unsuccessfully.
- Added packaged dependency presence checks and synchronized installer/application version.
- Added four regression guardrails for Windows packaging configuration.
- **Still unverified:** Windows CI execution, installer installation/uninstallation, DPI scaling, interactive GUI and upgrade behavior. The workflow must run on GitHub Windows runners to validate these.

# v0.42.0 — Phase 5 installer and updater foundation

- Added Windows one-folder PyInstaller build and Inno Setup installer/uninstaller configuration.
- Installer preserves user data by only uninstalling program files.
- Added Ed25519-signed manifest validation, version comparison, SHA-256/size checked installer download helper, and eight updater tests.
- Added manual Check for updates button, running checks in a background thread when official signing keys/feed are configured.
- Update button opens the official release download URL after explicit approval; it does NOT silently install updates.
- Signing key/feed are deliberately blank until official release infrastructure is set up. No unsigned updates accepted.
- Windows installer and GUI have NOT been run or verified in this Linux environment.
## v0.41.0 — Phase 4 regression checkpoint

- Export regression coverage for colliding sanitized animation names, empty timelines, and single-format export.
- Avoid overwriting separate animations when names differ only in punctuation or case.
- Source-level tests only; Windows GUI verification remains pending.

## v0.38.0 — Phase 4 GIF fidelity
Shared GIF palette, binary alpha, 10ms duration quantization, transparent-frame and motion regression tests. Windows GUI validation remains pending.

# v0.36.0 — Phase 4, Task 1: Sprite sheet timing fidelity

- Override generic sprite sheet export to preserve authored per-pose durations in the JSON manifest.
- Preserve exact RGBA frame pixels and explicit atlas rectangles, including configurable spacing.
- Add regression tests for atlas crops, multiple animation order, no-frame fallback, and non-mutating export.
- Phase 4 animated-format integration and Windows GUI verification remain pending.

## v0.37.0 — Responsive window hardening
- Scrollable left, middle and comparison panels for small viewports.
- Horizontal scrolling for crowded action toolbars.
- Restore saved windows inside available monitor bounds after resolution/monitor changes.
- Pure geometry tests for small, multiple and negative-coordinate displays.
- Actual Windows maximize/minimize behavior remains unverified until Windows GUI testing.

## v0.39.0 — Phase 4 APNG fidelity
- Isolated lossless RGBA APNG encoder; validate dimensions, timing and frame counts.
- Integration and byte-exact frame round-trip tests including alpha, motion and non-destructive export.
- Windows GUI and full end-to-end verification remain pending.

## v0.40.0 — Phase 4 Task 4: project-to-export integration
- Added end-to-end project save/reopen/export tests for GIF, APNG and PNG/JSON atlas.
- Verify multiple animations, per-pose timing, transparent RGBA pixels, atlas rectangles, looping and project fingerprint stability.
- Added a second nested-path save/reopen and separate-output-directory export regression test.
- Windows GUI and actual display testing remain outstanding.

## v0.43.0 — Windows update handoff and release assets
- Asynchronous verified installer download, save-before-update confirmation and Windows installer handoff.
- Offline signing script for a GitHub release manifest (Ed25519 private key never committed).
- Resource self-check for Slime Buddy, recipes and reference animations.
- Added signed-release and bundled-resource tests.
- Update feed and public key intentionally remain unconfigured until release owner provisions them.

## Phase 76 — Selected-layer X / Y / Rotation handles (2026-10-30)

- Draw three visible selected-asset overlays in canvas widget coordinates, not in exported sprite pixels.
- Yellow X controls horizontal movement, green Y controls vertical movement, blue R rotates around the selected artwork/joint; full X/Y drag still works on artwork.
- Edit Selection remains the only highlight-to-layer action and now toggles handles for already staged or committed layers without duplicating artwork.
- Show the active Asset Library layer and handles state prominently; keep pending Move Original transaction locked to its layer until Apply Move/Cancel.
- Preserve source-pixel erase at Apply Move, Copy Pixels, no automatic frame creation, and the original transform safety preflight.
- Add PySide6 GUI tests and Qt-free handle geometry tests; preserve all previous regression tests.

## Phase 83 — repeat selection and UI handle reset
- Restore source Asset Library selection after successful staged Apply Move/Cancel; maintain same-pose Slimer workflow.
- Remove old dashed box from highlight phase while preserving one X/Y/R handle during editable layer mode.
- Explain unsafe Move Original rejections without losing art or silently copying.
- Add regression tests and handoff.

## Phase 89 — Safe timeline reordering after Import Pose PNG
- Stabilize Qt timeline drag by suppressing drag-time current-row selection and deferring model reorder until after dropEvent completes.
- Preserve edited pose snapshots before moving pose IDs and durations; make timeline drag undoable.
- Block dragging while Slimer has an unconfirmed layer and make drop behavior explicitly non-overwriting.
- Add PNG import + timeline reorder Windows GUI regression. See `PHASE89_IMPORT_POSE_DRAG_REORDER_FIX.md`.
- Fix imported PNG leaking into Pose 1 through stale draft autosave when switching to newly added Pose 2.

### Phase 90 — Exact vs build-over PNG import; independent pose library
- Import Pose PNG now keeps the source PNG's exact RGBA pixels in its own pose; never auto-fills transparent black with opaque black.
- Added optional dropdown choice Build new pose over previous artwork, producing a single independently editable composite over a saved previous pose snapshot.
- Inactive inherited assets are hidden by default *in the current Asset Library view only*, with Show inactive to inspect/restore. Previous saved poses and their visibility are untouched.
- Import status reports opaque black pixel count to help diagnose the source file's actual transparency.
- Added deterministic model alpha/isolation/roundtrip tests and Windows GUI import/visibility tests. Slime Cleaner remains a separately tracked issue.

## Phase 91 (2026-10-31): no reference UI
- Removed all external-reference viewing/upload/playback and guidance; retained editing previews and actual artwork imports.
- Replaced reference synchronization helper with simple saved-creature frame timing.
- Corrected Phase 88's empty-animation test lookup; full headless regression remains green.
- Source package and detailed test notes: `PHASE91_REMOVE_REFERENCE_FEATURES.md`.

## Phase 92 (2026-10-31): Preserve previous editable pose on Place Frame
- Fix Place Frame flattening the **previous** saved pose while adding a combined source to the new pose. Previously saved poses retain independent editable Slimer layers and their PNG snapshots; only the new pose receives one merged artwork layer.
- Correct Windows Phase 88 regression to expect alpha 0 at the old Move Original coordinate, unchanged alpha at the +3 moved destination, and independently editable prior pose layers.
- Added save/reopen and cross-pose transparency/layer-preservation regression. No reference features restored, no Slime Cleaner destructive changes.
- Details in `PHASE92_POSE_SOURCE_PRESERVATION.md`.

## Phase 93 (2026-10-31): Prevent cross-pose overwrite after Place Frame
- User manually reported Phase92's *real* Swordcat workflow failed after Pose 2 editing/Place Frame: Pose 1 displayed Pose 2's later artwork. Previously passing GUI tests did not constitute acceptance.
- Replaced row-only GUI draft ownership `(project, animation, index)` with stable pose identity `(project, animation, index, pose_id)`. Auto-save resolves the currently owned pose by its stable ID and refuses to write if the live canvas belongs to a different pose.
- `select_step`, `load_frame`, project activation and PNG edit reloading bind live canvas to the exact loaded pose; switch to an empty animation resets ownership.
- Added `_canvas_owns_selected_pose` gate to Place Frame, Save Current Pose, Insert Pose, Copy Pose, Duplicate Pose and per-pose asset visibility changes; a stale selection fails closed rather than using pixels from another pose.
- Updated old source-text contracts for the new identity-based loader without weakening their ordering requirements.
- Added Windows GUI regression `tests/test_phase93_pose_identity_gui.py` that creates three distinguishable poses with Slimer moves and verifies Pose 1 survives editing Pose 2 then placing Pose 3, plus stale GUI row protection. Added headless model save/reopen regression for three distinct poses and their pose IDs.
- Local full suite: 497 passed, 41 skipped, 12 subtests passed. PySide6 GUI tests must be run on user's Windows machine and real-artwork workflow manually confirmed before declaring fix accepted.
- Slime Cleaner remains independently unresolved; reference-only features stay removed. Earlier ZIPs, projects and GitHub untouched.

## Phase 101 — Center Canvas Chrome + Single Slime Buddy Toggle (2026-10-31)
- Design-only canvas/view/project-tab visual polish using CSS selectors with object names. No new controls or tool functionality.
- Removed duplicate Buddy workspace ON checkbox per artist request. Retained one top Buddy ON/OFF switch with original persisted effect.
- Updated obsolete Phase79 GUI/source and Phase99 signal count tests to reflect the explicitly retired duplicate checkbox links.
- Verified 153 unchanged Suite non-constructor methods and unmodified canvas methods; 514 local pytest pass, 49 skipped.
- Phase 98 known-good rollback and earlier phase ZIPs remain untouched.

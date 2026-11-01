## v0.47.0 — Windows GUI smoke-test hardening

The packaged GUI smoke test now checks actual minimize/maximize states, restore-to-normal, and resize behavior against available screen geometry at 800×600, 1280×720 and 1920×1080 targets (clamped to runner screen). Windows CI logs Qt and OS diagnostics. These tests require execution on a Windows runner; they have not been executed in this environment.

# Product requirements — discussed and agreed

## Identity & separation
- Standalone **Slime House Friendly Animator**, fresh version 0.1.0; independent Windows EXE and own version history.
- Original Slime House Studios stays unchanged until Friendly Animator is verified; later remove duplicated Desktop Pet Animator only.
- Authoring tools only; desktop-pet gameplay remains a separate future project.

## Interface
- Cozy dark/slime-green design, readable fonts, fun icons, tooltips, optional Slime Helper, beginner-first.
- Left asset library (PNG imports, categorization, reusable parts); top center per-animation instructions and generated framework; bottom center large editable sprite-sheet workspace; right synchronized generic target animation vs live creature preview.
- Expandable/maximizable panels; Easy and Advanced modes; hide advanced options, never lose project data when switching.

## Asset editing
- Resize every asset on import and after; nearest-neighbor pixels, numeric size, drag resize handles, optional aspect lock, reset to untouched original, rotate, flip, layers and ordering, pixel edits, precise anchors.
- Multiple creature types: biped, quadruped, winged, floating, crawling, slime, custom; rigging pivots, optional joints and IK.

## Animation
- All 31 everyday action recipes plus custom templates; required/optional parts, frame-by-frame instructions, editable steps, reference animations appropriate to body type.
- Drag-to-place poses, duplicate/reorder frames, durations, timeline, onion skin, smooth preview, ghost overlay, transitions, validation warnings and nonblocking assistance.
- Per-creature animation library, context-sensitive tools, friendly terms, guided wizard, optional tips.

## Reliability & export
- Full undo/redo, autosave/crash recovery, portable save/reopen including untouched originals, rigs, all poses and frames; project backups.
- Export transparent PNGs, fixed-grid and optionally packed sprite sheets with JSON, GIF, APNG, batch export, optional hitboxes/anchors, selectable frame sizes.
- Windows maximize/resize stability, test GUI and exports on Windows; build separate EXE through GitHub Actions.

## Open source integration
- Pillow, PySide6 graphics, NumPy and rectpack where useful; evaluate PyQtGraph; study LibreSprite UX but do not copy GPL code without a license decision.

## Acceptance test
Create creature -> import and resize parts -> set anchors -> select animation -> follow frame template -> edit poses -> compare reference -> preview -> save/reopen -> export. Preserve sharp pixels and all original assets.

## v0.17.0
Periodic recovery snapshots and startup restore/discard dialog implemented; broader multi-document management remains planned.

### v0.20.0
Project tab close confirmation and per-project frame/selection restoration added. Future work: accurate dirty-state tracking, multi-project autosave and recovery, Windows GUI smoke tests.

## v0.20.0
Each open creature now gets its own crash-recovery snapshot. Startup offers to restore all recovered creatures in separate tabs; saving or closing a creature discards only that creature’s recovery copy.


Phase 1 Task 2: Beginner quick-fix buttons for flip, center and original-size restore; keep controls in left panel.

## Creative freedom
Guidance teaches tools and technical workflows, never dictates creature anatomy, aesthetics, proportions, or motion style.


### v0.25.0 Slime Buddy
Optional collapsible, station-based instructions for Import, Assembly, Rigging, Poses, Timeline, Compare, Save, and Export. Advice is procedural and never dictates character design.


Phase 1 task 5: layer-order, rig attachment, undo/redo, saved pose and save/reopen integration regression tests. Cyclic attachment validation prevents partial movement.

### Slime Buddy motion coaching
Guidance must be optional, non-prescriptive and body-type-aware; no visual scoring, anatomical assumptions or automatic artwork corrections.

Phase 4 APNG: lossless RGBA export with authored frame timing and infinite looping, regression-tested at source level.

Phase 4 Task 4 source checkpoint (v0.40.0): end-to-end save/reopen/export regression tests cover PNG/JSON sprite sheets, GIF, APNG, multi-animation timing, and non-destructive exports. Phase 4 Task 5 full regression and Windows integration remain pending.


Phase 5 release gate: successful Windows runner installation, installed EXE startup, minimize/maximize smoke, uninstall, manual DPI/monitor testing, and verified updater configuration.

Phase 5 v0.46.0: Windows CI same-version reinstall and user project preservation test added; cross-version upgrade remains pending.

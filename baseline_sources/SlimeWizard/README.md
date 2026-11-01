## v0.47.0 — Windows GUI smoke-test hardening

The packaged GUI smoke test now checks actual minimize/maximize states, restore-to-normal, and resize behavior against available screen geometry at 800×600, 1280×720 and 1920×1080 targets (clamped to runner screen). Windows CI logs Qt and OS diagnostics. These tests require execution on a Windows runner; they have not been executed in this environment.

## v0.46.0 — Windows upgrade test checkpoint

GitHub Actions now tests a same-version installer reinstall, verifies the packaged GUI after each installation, uninstalls, and checks that a user-project sentinel outside the application directory remains byte-for-byte unchanged. A real older-to-newer version upgrade, actual Windows execution, DPI tests and update-feed signing are still outstanding.

## v0.41.0 — Phase 4 regression checkpoint

- Export regression coverage for colliding sanitized animation names, empty timelines, and single-format export.
- Avoid overwriting separate animations when names differ only in punctuation or case.
- Source-level tests only; Windows GUI verification remains pending.

## v0.38.0 — Phase 4 GIF fidelity
Shared GIF palette, binary alpha, 10ms duration quantization, transparent-frame and motion regression tests. Windows GUI validation remains pending.

# Slime House Friendly Animator — v0.27.0

Standalone native PySide6 creature-animation authoring tool. Original Slime House Studios is unchanged.

## Run

```bash
pip install -r requirements.txt
python friendly_animator.py
python -m unittest discover -s tests -v
```

## Included

Four-panel friendly workspace; PNG import and nearest-neighbor resizing; canvas dragging, resizing and rotation; joints and linked body parts; frame-specific poses; thumbnail timeline; per-pose timing; 31 everyday animation recipes; preview with speed and loop controls; save/reopen; sprite-sheet PNG+JSON export.

## Still in development

Windows GUI and EXE unverified. Anatomy-specific reference animations, complete undo/redo, autosave/recovery, full pixel editing, GIF/APNG, and advanced rigging are not finished.


## v0.13.0 workspace tabs
Use the tabs below the canvas to switch between animation and phase views. The + menu opens more animation or phase tabs. The project tab is an overview of the currently opened creature; it is not yet a multi-document manager.

## v0.27.0

Comparison panel is compact by default and can be hidden with the eye button. Right-click a bottom tab to close the view without deleting its animation. Panel layout is remembered between launches.

## v0.27.0
The compact comparison panel now renders offline pixel-art example poses for all recipes and follows playback. These are generic demonstrations rather than exact targets for every creature body type.

## v0.27.0
The compact comparison panel can show biped, quadruped or floating schematic motion references. The main canvas shows a short contextual pose hint. These are guidance, not automatic pose validation.

## v0.27.0 crash recovery
When assets are present, a recovery copy is saved once per minute in the OS temporary directory. On the next launch, you can restore or discard it. Saving explicitly clears the recovery copy. Recovery is not a substitute for regular project saves.


## v0.27.0
Open multiple creature projects from the top bar or + tab menu. Click project tabs to switch between separate models. Project tabs cannot yet be closed; save each creature separately.

## v0.27.0
Right-click a creature tab to close it after confirmation. Project switching preserves selected asset and animation pose memory. Exiting with imported parts asks for confirmation. These are conservative prompts, not full dirty-state tracking.

## v0.27.0
Each open creature now gets its own crash-recovery snapshot. Startup offers to restore all recovered creatures in separate tabs; saving or closing a creature discards only that creature’s recovery copy.

## Animated export
Use **Export GIF / APNG** to render each saved animation into a looping GIF and transparent APNG. The existing sprite-sheet export remains available. GIF has palette limitations; APNG preserves RGBA pixels.


Phase 1 task 1: Undo/Redo supports Ctrl+Z, Ctrl+Shift+Z and Ctrl+Y, and separate history per open creature.


### Phase 1 Task 2
Select an asset, then use QUICK FIXES in the left panel. All operations can be undone with Ctrl+Z.

## v0.27.0 pose editing
Edit a saved pose using drag/resize/rotate and switch frames; the draft is preserved for that pose only. Generic examples are optional inspiration and never enforce anatomy or appearance.


### v0.27.0 Slime Buddy
Optional collapsible, station-based instructions for Import, Assembly, Rigging, Poses, Timeline, Compare, Save, and Export. Advice is procedural and never dictates character design.

## Canvas navigation
Mouse wheel zooms at pointer. Middle-drag or Ctrl+left drag pans. Fit to Canvas resets view; view settings are remembered per creature. Zoom does not change exported pixel sizes.


Phase 1 task 5: layer-order, rig attachment, undo/redo, saved pose and save/reopen integration regression tests. Cyclic attachment validation prevents partial movement.


## v0.28.0 Phase 2 checkpoint
Motion reference examples now vary by action for quadruped and floating creatures. They are schematic optional examples, not prescribed anatomy.

## v0.29.0 Phase 2 checkpoint
Optional technique coaching covers all 31 recipes and four body contexts. Guidance never enforces anatomy, style or reference fidelity. Windows GUI still requires verification.

## v0.30.0
Phase 2 Task 3: optional neighboring-pose ghosts, total-duration feedback, saved-pose still preview, persistent Slime Buddy toggle.

## v0.31.0 technical checks
Click **Check animation readiness** for optional, non-destructive warnings about missing assets, missing frames, mismatched parts, or timing. No artistic grading or automatic edits.

## v0.32.0
Phase 2 Task 5 adds shared-clock synchronized reference and creature playback. See CHANGELOG.md.


v0.33.0 Phase 3 checkpoint: project-scoped animation tabs; closing a creature clears its associated animation tabs; restores selected asset on project switch. Automated workspace identity tests. Windows GUI validation pending.


## v0.34.0 safety update
Closing modified creature tabs or exiting now offers Save, Discard, or Cancel. Saving an untitled creature requests a destination. Failed or cancelled saves prevent closing. Windows GUI testing remains pending.


Phase 3 v0.35: autosave recovery hardening, window geometry restoration, rename and duplicate-open safeguards.

## Phase 4 checkpoint (v0.36.0)
Sprite sheet PNG/JSON exports now include each authored pose duration, not a fixed placeholder. Automated tests compare each atlas crop against the rendered pose. Windows GUI verification remains pending.

Phase 4 APNG: lossless RGBA export with authored frame timing and infinite looping, regression-tested at source level.

### v0.40.0 verification
Run `python -m unittest discover -s tests -q` to exercise the project save/reopen and GIF/APNG/sprite-sheet export integration suite. These are headless model tests; Windows GUI validation is not yet complete.


## Windows installation and updates (v0.42.0 foundation)

GitHub Actions now builds a **one-folder portable distribution** and an **Inno Setup installer**. The installer includes uninstall support and does not delete user-created project files. Windows builds require Inno Setup 6 on the runner.

The in-app **Check for updates** control is manual. It remains disabled until `studio/release_config.py` is configured with an official HTTPS manifest URL and an Ed25519 public signing key. A signed update manifest must contain `payload` and `signature`, with `payload` containing `version`, `installer_url`, `sha256`, and `size`. The signature covers canonical sorted compact UTF-8 JSON for `payload`. Private keys must NEVER be committed. A future release should add nonblocking verified-download progress and installer handoff; currently approved updates open the official release download URL.

No claim of a working Windows installer is made until GitHub Actions builds and Windows smoke tests pass.

### Release signing and updates (v0.43.0)
Build the Windows installer via GitHub Actions. Release owner must provision an offline Ed25519 signing key, publish the installer on GitHub Releases, generate `update.json` using `packaging/sign_release.py`, and embed the matching public key and HTTPS feed in `studio/release_config.py` for a subsequent build. **Never commit the private key.** Users approve downloading and launching a verified installer; unsaved projects are protected before handoff. No silent updates. This workflow still requires live Windows verification.

### Windows packaged GUI smoke test (v0.44.0)
The Windows workflow builds the one-folder EXE, then runs `SlimeHouseFriendlyAnimator.exe --smoke-test` to exercise startup, minimize/maximize/restore and offline bundled resources. This test does not substitute for interactive multi-monitor/DPI, installer, updater or export verification.


### Windows installer lifecycle verification (v0.45.0)
The Windows GitHub Actions workflow builds the one-folder app and Inno Setup installer, launches the portable GUI smoke test, silently installs into a temporary runner directory, launches the **installed** GUI smoke test, then uninstalls and checks the executable was removed. Check the GitHub Actions run logs for actual results; these checks cannot be claimed passed until run on Windows.

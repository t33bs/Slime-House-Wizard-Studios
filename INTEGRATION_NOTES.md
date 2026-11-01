# SHWS Build 1 — integration boundary and future development

## Completed in source candidate

- Parent `QMainWindow` with native `QTabWidget` containing complete SHS and Slime Wizard editors.
- SHS remains in its original `studio` namespace; Wizard's runtime is under `shws_wizard.studio` to prevent collisions between model files with the same names.
- Wizard timeline-drag ownership resolves the nearest Wizard editor widget rather than the outer parent window.
- Wizard's `Edit Frame in SHS` action routes to the SHS tab using a PNG bridge; it no longer needs a separately installed SHS application.
- Wizard's existing `Reload SHS Edit` validates project/animation/pose and image canvas size. SHS will refuse the handoff if there is a dirty document that would be overwritten.
- Host close calls both editors' pre-existing unsaved-work checks and honors cancel.
- Source baselines are included for regression purposes. No original repository was changed.
- Windows workflow includes both portable onedir distribution and Inno Setup installation plus uninstall smoke test.

## High-priority manual validation required

The two legacy applications were originally standalone `QMainWindow` implementations. Nesting them as child tabs uses Qt-supported widget composition, but their focus-sensitive shortcuts, dock state, context menus, geometry restoration, child-window dialogs, and layered timeline drag/drop must be validated in a real Windows GUI. A green source smoke test does not validate those interactions. Do not publish the EXE as stable before these checks pass.

Some preferences are stored in original per-editor `QSettings` namespaces. Existing preferences could carry into the combined app; test first launch on a clean user profile and on a profile that has both standalone versions installed.

## Future Slime Buddy integration (NOT included)

The independent Slime Buddy AI generator stays in its separate repository. In a future release, interface with Buddy through a separately launched worker process and a versioned request/response protocol. Give local AI an explicit opt-in switch. Admission control should calculate estimated VRAM requirements before scheduling jobs, target a configurable **~5 GiB GPU budget**, serialize concurrent inference, and reject or fall back when free GPU memory or an AMD-compatible backend is insufficient. A 5 GiB application budget is **not** a guaranteed hard device-memory cap without driver/backend enforcement; test on the user's Radeon RX 5600 XT 6GB. Keep all manual SHS and Wizard features usable without any model or online API.

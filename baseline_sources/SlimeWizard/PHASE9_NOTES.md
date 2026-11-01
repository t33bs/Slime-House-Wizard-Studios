# Phase 9 source beta

Changes:
- Pose snapshots now retain each layer's source pixel PNG, so Move Original cannot silently overwrite the artwork of previously saved frames. Earlier v0.47 poses without embedded source PNGs still load using legacy behavior; the change cannot recover pixels already overwritten in old saved poses.
- Added model regression test for distinct pose pixels, reloading a previous pose, and save/load persistence.
- Slimer: Finish Selecting -> Move, Edit Selection toggle, faint 10%-opacity highlight in paint mode, no colored overlay in transform mode.
- Existing Ghost nearby poses checkbox continues to display prior frames only in the editing canvas (never exported).
- Preview: + / - / Fit zoom controls with nearest-neighbor scaling and scrollable view.
- Choose Animation and Follow Recipe independently collapse; state persisted in QSettings.
- Slime Buddy guidance moved to the comparison dock with a retro text mascot panel; existing on/off preference retained.
- Export Frame PNG button for editing in Slime House Studios.

Validation: 141 automated model tests pass; Python compilation passes. PySide6 GUI interaction and Windows installer/portable builds are NOT tested in this environment. UI/UX and full workflow still require user beta verification.

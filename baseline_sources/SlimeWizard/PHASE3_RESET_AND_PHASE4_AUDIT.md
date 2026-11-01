# Roadmap audit — Phase 3 reset fix and Phase 4

## Implemented now
- Clear cached per-phase Slimer transforms when switching creatures/poses/projects.
- Clear cached per-phase transforms when activating a new Slimer session.
- Added regression contract for both reset paths.

## Phase 4 audit
- Already implemented: independent per-phase highlight masks, colors, and transform values; selectable phases via dropdown; custom phase creation.
- Not yet implemented: separate visible tabs for each used highlight color (currently dropdown). Avoid duplicating the existing mask/transform engine.
- Windows-only verification queue: switching between selections, preserving transforms, no preview over painting, visible handles after Finish Selecting, pose/project isolation, project reopen and exports.

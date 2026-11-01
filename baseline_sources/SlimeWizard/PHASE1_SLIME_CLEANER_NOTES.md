# Phase 1 partial: Slime Cleaner

- Removed Move Original checkbox and automatic source-clearing from Slimer placement.
- Added independent Slime Cleaner brush tool, adjustable size, transparent pixel clearing and stroke-level undo snapshot.
- Cleaner targets topmost visible opaque layer per pixel; does not touch hidden layers.
- Slimer and Cleaner are mutually exclusive editing tools.
- This is NOT the full Phase 1 frame-independence or multi-selection repair.
- Test on a disposable project; Windows GUI build not verified here.

# Slime Wizard Phase 91 — Remove Reference Features

## User decision
Never show or import external reference imagery in Slime Wizard. Keep normal source-artwork import (Import PNG assets, Import Asset, and actual editable pose PNGs) and previewing of the user's **own** creature/poses. The distinction is crucial: a working sprite PNG is not a reference image.

## Code changes
- Deleted external reference-only controls, parsing, timers, and renderer from `friendly_animator.py`.
- Removed `studio/user_reference.py` and `studio/comparison_sync.py` (which mapped an animation to external reference-frame counts).
- Added `studio/preview_timing.py` for timing the user's saved pose preview without reference playback.
- Replaced Slime Buddy `Compare` station with `Preview` and changed its tips to discuss only current animation.
- Updated visible pane heading and show/hide text to `Animation Preview` / `Hide previews` / `Show previews`.
- Replaced obsolete tests that demanded reference UI with guards that forbid reintroduction; added Windows GUI smoke test.
- Corrected the previous Phase 88 test `KeyError: 'Idle / Breathing'` by checking an empty animation with `.get(...)` instead of indexing an uncreated key. No pose model logic was modified to paper over the test.

## Verification
- Source compiles.
- Linux/headless full suite: **495 passed, 40 skipped, 12 subtests passed**.
- PySide6 Windows GUI tests skipped locally because PySide6 is not installed. Must run on user's Windows computer.

From the extracted source folder in PowerShell:

```powershell
& "$env:USERPROFILE\Downloads\DocumentsSlime-Wizard-Pre-Merge-Backup\.venv\Scripts\python.exe" -m pytest -q tests/test_phase91_no_reference_gui.py tests/test_phase88_first_place_frame_gui.py tests/test_phase86_repeat_alpha_gui.py
```

Then launch:

```powershell
& "$env:USERPROFILE\Downloads\DocumentsSlime-Wizard-Pre-Merge-Backup\.venv\Scripts\python.exe" .\friendly_animator.py
```

## Manual checks
- No `Show my animation reference` checkbox or reference image uploader appears; real creature preview and Slimer preview still work.
- `Import PNG assets` and `Import Asset` still import editable creature art.
- Make Pose 1 Slimer changes, Apply Move, Place Frame, then perform another Slimer edit; previous pose remains recoverable with its saved layers.
- Confirm Slime Buddy only guides tools, never aesthetics or external references.

## Open issues
- **Slime Cleaner** malfunction on transformed or overlapping artwork; user has not given exact reproduction. Preserve pixel integrity, undo, and pose isolation when fixing.
- **Import Pose PNG** remains an actual artwork import operation, not a reference feature; user and assistant explicitly distinguished these. Its behavior was discussed in Phase 90, but no extra changes were made in Phase 91.
- GitHub not touched, no commits/pushes; previous source ZIPs left intact.

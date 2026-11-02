# Build 1.8.2 — SHS → Slime Wizard: Add as New Pose

## Why
Build 1.5–1.8.1 introduced **Save Back to Animator + Return to Wizard** only for a *linked* existing pose, after selecting **Edit Frame in SHS** from Wizard. It replaces exactly that original pose and is deliberately hidden when SHS is not editing a linked frame. This is not the same as creating a new pose from ordinary SHS artwork.

## New visible control
In the **combined** Slime House Wizard Studios application, open the **SHS Studio** tab. In the left sidebar, immediately below the Save Back control, the new button is always visible:

**Send to Slime Wizard as New Pose**

This captures the currently displayed SHS image, transfers it in memory to the active Wizard animation, inserts it *after* the selected Wizard pose (or as pose 1 if the timeline is empty), selects the new pose, and returns to the Wizard tab. It creates a distinct editable RGBA image asset and stable pose ID; it never overwrites a previous pose. Existing frame IDs, PNGs, and timings remain unchanged. Undo remains available via Wizard's normal history. Then use **Save Creature** / **Save Creature As** to persist the `.rig.json` project.

## Safety rules
- SHS and Wizard canvases must match pixel dimensions exactly (for example, both 128×128). No automatic stretching, cropping, or forced resizing.
- Any unfinished Wizard Slimer operation or unplaced next pose blocks transfer, as does a mismatched currently selected timeline pose.
- A failed validation does not change or add Wizard frames and does not switch tabs.
- Successful *new-pose* transfer ends any old SHS linked-frame session to avoid a later accidental overwrite of the old pose.
- The old linked **Save Back to Animator + Return to Wizard** remains available when the user started from Wizard **Edit Frame in SHS**; it still updates only that existing pose.
- The new button exists in the **combined application SHS tab**, not the older standalone SHS executable.

## Regression tests
`python -m pytest -q tests`

- New-pose import checks 0, 1, 6, 7 and 12 saved poses, including insertion in the middle.
- Pixel-exact RGBA round trip, original pose images, stable IDs, timings, saved/reopened project.
- Rejects unfinished Slimer layer/part, unplaced next pose, wrong canvas dimensions, invalid image, wrong pose owner.
- Tests host callback behavior on failure/success; linked original pose is only released on success.
- Windows Qt offscreen smoke checks the button visible and clickable in the actual combined SHS editor. This test skips when PySide6 is unavailable locally.

Result in current environment: **65 passed, 7 skipped (Qt tests require PySide6/Windows verification)**.

## Update order and Build 1.9 warning
Apply Build 1.8, **then** Build 1.8.1, **then** Build 1.8.2 if the repository is currently on earlier source. Do not use this as a replacement for the initial Build 1.8 callback change. Build 1.9's previously packaged APNG patch includes copies of both `main.py` and `shws_wizard/friendly_animator.py` and WILL overwrite the new-pose additions if applied afterward. Reapply the Build 1.8.2 patch after the old Build 1.9 patch, or use a later combined release that merges both features. Do not commit either until local changes are reviewed in GitHub Desktop.

Standalone Slime Buddy project remains separate and unmodified.

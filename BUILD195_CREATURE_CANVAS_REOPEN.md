# Build 1.9.5 — Creature Canvas Reopen

## User report

The Open Creature dialog displayed:
`Cannot open creature: canvas size must contain width and height. The project was not changed.`

## Distinguishing the two kinds of JSON

`Save Creature` writes a valid version-3 editable `.rig.json` with `size: [w,h]`, per-frame layer states, pose identities, and asset directory. `Export Sprite Sheet` separately writes `*_sheet.json`, which has `frame_size`, `sheet_size`, and `frames`. The old Open Creature filter accepted either file, then rejected sheet metadata with a misleading canvas-size error.

## Changes

1. Open dialog prefers `.rig.json`; legacy creature `.json` remains selectable.
2. Detect sheet manifests explicitly and show an actionable 'this is export metadata' error; never invent missing editable layer data.
3. Normalize explicit alternate canvas dimension encodings in-memory for genuine legacy editable rigs (`size` object, `canvas_size`, `canvas`, or `canvas_width/canvas_height`). No inferred dimensions from a PNG because source images may be smaller than the canvas.
4. Preserve previously saved pixel data, animation poses, IDs, frame timings and the original source manifest. No automatic resize or resave.
5. Run cross-canvas-size regression and Qt offscreen open test on Windows.

## Windows acceptance

- Start with an empty default 128x128 creature. Use Open Creature to select a saved 256x128 rig. The new tab must display the correct 256x128 canvas and all existing timeline poses.
- Check non-square 96x160 and square 512x512 files. Save As and reopen to verify dimensions still match.
- Attempt to open a `*_sheet.json`. Expect a clear explanation to open a `.rig.json` instead, with the current project unchanged.
- If a genuine `.rig.json` still fails, copy its JSON and corresponding `_assets_...` folder to inspect missing or nonstandard size metadata; never overwrite the original.

## Scope

SHS editor, Chameleon, reference window, Slimer/Cleaner, export renderers, original standalone Wizard baseline, and independent Slime Buddy source are unchanged.

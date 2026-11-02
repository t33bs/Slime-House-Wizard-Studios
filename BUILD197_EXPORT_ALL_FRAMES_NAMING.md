# Build 1.9.7 — Export All Frames naming cleanup

## Reason
Build 1.9.6 still suggested the obsolete `friendly_frames` name, and its
individual-frame exporter embedded animation labels (sometimes containing old
reference/project titles) into each PNG filename.

## Behavior
1. **Export All Frames** prompts for a JSON frame-set name, starting with
   `creature_frames.json`, not `friendly_frames` or an imported filename.
2. Name the set, e.g. `SwordcatWalk_frames.json`. Exports:
   `SwordcatWalk_frame_0001.png`, `SwordcatWalk_frame_0002.png`, ... plus
   `SwordcatWalk_frames.json`.
3. Numbering is consecutive across all animations. The manifest still stores
   each image's original animation label, index, timing and 128×128 or other
   saved canvas dimensions for a faithful editable-frame reimport.
4. Filename prefix is determined ONLY by what the user types in the dialog;
   not original asset names, saved project names, reference names, or animation
   names. Invalid Windows characters are normalized; reserved names refused.
5. **Export Frame PNG** also no longer defaults to `friendly_frame_...`;
   it suggests `creature_frame_0001.png` instead.

## Scope and integrity
- Source pixels, layers, frame order, frame identity and timestamps are unchanged.
- GIF/APNG and sprite sheet exporter behavior is unchanged.
- The standalone Slime Wizard and SHS baseline source snapshots are unchanged.
- Existing `*_frames.json` manifests remain importable as before.
- The new naming applies to NEW frame exports; old files on disk are not renamed.

## Windows acceptance
1. Load a multi-pose `.rig.json` and select Export All Frames.
2. Type `MyNewWalk_frames.json` in a temporary folder; export.
3. Check `MyNewWalk_frame_0001.png`, `_0002.png` ... and
   `MyNewWalk_frames.json` exist; no `friendly_` filenames.
4. Open the JSON frame manifest with Open Creature; check poses, timing and
   independent editing. Use Save Creature As to save a new `.rig.json`.
5. Repeat with a different name; ensure no old project/reference titles appear.
6. Confirm Export Frame PNG suggests `creature_frame_0001.png`.

Local CI: Run `python -m pytest tests -q` and source compilation.
Qt UI tests require GitHub Windows Actions / user manual acceptance.

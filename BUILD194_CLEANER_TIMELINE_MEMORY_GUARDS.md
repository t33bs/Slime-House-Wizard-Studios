# Build 1.9.4 — Cleaner multi-pose protection

## Reproduction and cause

In Build 1.9.3 `Suite.cleaner_paint` set `_next_pose_capture_pending=True`
after erasing pixels on a normally selected SAVED pose. Subsequent
`load_frame` calls refused to load ANY selected pose as long as that bit was
set. The timeline could highlight a different thumbnail while the canvas
still displayed the former pose. The Undo path restored the model, but never
cleared that transient bit, producing the partially restored UI the user saw.

The issue appeared after many edits in the Windows portable build. The
history also allocated complete project snapshots on every mouse press,
even when clicking transparent pixels, and re-rendered on every hover/stroke.
The precise memory-leak hypothesis is **unconfirmed**; history is capped at
100 entries and no unbounded growth was demonstrated. This fix reduces needless
allocations but is not a proof against every long-session problem.

## Fix scope

- Cleaner only edits the identity-verified current pose, or a separately
  existing genuine Slimer draft. It never creates next-pose mode by itself.
- Undo/Redo clears stale transient draft flags before loading the selected
  pose so a timeline selection cannot silently remain on an old canvas.
- Capture one Undo snapshot immediately before the first actually erased
  pixel per mouse stroke; transparent misses create no Undo entries and do
  not disturb Redo. No-op Cleaner inputs skip costly repaint/preview work.
- Saved frame source PNGs stay separate; nothing auto-erases detached shadows.
- Keeps `Move Original`/`Copy`, Place Frame, pose histories, APNG export,
  references, and SHS → Wizard transfers untouched.

## Validation

- Local integration suite: 82 passed, 10 PySide6 GUI tests skipped locally.
- Long synthetic regression: 24 distinct poses + 50 Cleaner operations;
  all pose IDs and non-target images remain intact.
- Actual user-supplied nine-pose Swordcat rig: 17 layers, 27 successful
  Cleaner operations on a temporary copy, saved pose IDs/durations stable,
  original file untouched. Python tracemalloc peak about 15.5 MB in that
  limited regression; not equivalent to Windows process working-set memory.
- Windows-only offscreen GUI test: staged in
  `tests/test_build194_cleaner_windows_gui.py`. Run it via GitHub Actions;
  confirm real mouse/toolbar interaction in the portable build manually.

## Manual test

1. Back up the rig JSON and matching assets folder.
2. Open a creature with 8+ different saved poses. Switch to pose 7.
3. Activate Slime Cleaner; erase one **intended** pixel. Switch to poses
   1, 3, 8 and 7. Every canvas should correspond to the highlighted frame.
4. Undo and repeat switching, then Redo and switch again.
5. Use Cleaner on transparent space, then Undo; it should not undo an earlier
   unrelated edit (no empty history entry).
6. After 20–50 strokes, save as a new `.rig.json`, close and reopen. Confirm
   all poses remain distinct and frame timings unchanged.
7. Make an intentional new unplaced pose with Slimer: it must **still** require
   Place Frame (or Save Creature for draft persistence) before switching.

**Do not mark as a fully verified Windows bugfix until the GUI test and a
manual long-running portable session pass.**

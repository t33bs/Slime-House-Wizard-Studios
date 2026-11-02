# Build 1.9 — pixel-exact APNG and optional detached-pixel notice

The earlier APNG encoder used `disposal=2` (`PREVIOUS`) on full independent
RGBA canvases. The original nine-frame Swordcat sheet reproduced the bug:
only the first two decoded frames matched, while later frames lost the upper
sprite. Changing to `disposal=1` (`BACKGROUND`) with `blend=0` (`SOURCE`)
preserved all nine frames pixel-for-pixel and kept timing at 125ms.

Changes:
- Full-canvas RGBA APNG export with correct disposal and blend.
- Atomic output: encode into a neighbor temporary file, open it, verify all
  frame RGBA bytes, durations, loop, and count. Replace the existing APNG only
  after verification; remove the temporary file on failure.
- A narrowly scoped, **non-destructive** optional export notification detects
  small 8-connected pixel islands detached from a dominant sprite. It never
  changes art or blocks export; islands can be intentional effects.
- Added synthetic nine-frame regression with duplicate first pose, atomic
  failure recovery, and isolated-pixel tests, without bundling any user art.

Verification on user's provided `testerfester_sheet.png` and reconstructable
`placeframe.copy.rig.json`: all **9** frames matched the rig and sheet exactly,
including their transparency and 125ms timing. The optional check identified
10 isolated pixels at x=49–58, y=118 on pose 9. No art was modified.

Local integration result: **52 passed, 6 skipped** (Qt-only GUI tests).
Build 1.9 incorporates all Build 1.8 handoff fixes and prior builds.

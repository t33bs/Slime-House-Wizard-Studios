# Phase 14 — Playback clock correction

- Replaced hard-coded 25 ms advancement per Qt timer event with monotonic elapsed time.
- Resuming playback resets the clock baseline so paused time is excluded.
- Changing playback speed or repeat mode restarts the animation and clock baseline.
- Added deterministic unit tests for irregular timer intervals, pause/resume, and clock anomalies.
- Existing duration data, animation export, and pose editing were not modified.

## Deferred Windows GUI checks
- Confirm 0.5x, 1x and 2x playback under normal load and when the UI is busy.
- Pause for several seconds, resume, and verify no unexpected frame jump.
- Verify non-looping animations stop on the final frame.
- Verify pose duration edits update the preview as expected.

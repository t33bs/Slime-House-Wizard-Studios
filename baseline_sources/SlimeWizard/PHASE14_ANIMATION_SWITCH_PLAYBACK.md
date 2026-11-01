# Animation switching playback audit

- Corrected `change_anim` to call `restart_playback`, resetting elapsed preview time and rebasing the monotonic clock, then refresh the destination animation preview.
- Corrected `restart_playback` to pause its clock when the Play button is unchecked.
- Added source-level regression checks in `tests/test_animation_switch_playback.py`.
- No pose data or pixel manipulation logic changed.
- Windows interaction verification is deferred to `PHASE1_DEFERRED_WINDOWS_TESTS.md`.

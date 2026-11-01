# Phase 14: Non-looping playback completion / resume

Fixed a real timeline playback gap: a completed non-looping animation previously kept its elapsed time at the final boundary, so pressing Play again immediately stopped it. New `studio/playback_resume.py` helper restarts only completed non-looping playback. Mid-animation pause/resume and looping playback retain their elapsed time. Empty timelines do not start the clock. Added four unit tests. Windows GUI checks are deferred to PHASE1_DEFERRED_WINDOWS_TESTS.md.

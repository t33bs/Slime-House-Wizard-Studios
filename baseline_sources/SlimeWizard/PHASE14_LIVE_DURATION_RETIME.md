# Phase 14 — Live duration edits

The duration editor now consumes outstanding clock time and rebases preview elapsed time against the edited timeline. If playback is within the edited pose, it keeps the fractional progress through that pose. If playback is after the edited pose, it shifts by the duration difference. Loop cycles are retained. The existing model, exports, and saved pose format are unchanged.

GUI verification is deferred to the Windows checklist.

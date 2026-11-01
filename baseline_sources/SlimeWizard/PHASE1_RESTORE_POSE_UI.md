# Phase 1: Restore Previous Pose UI

- Added Restore Previous Pose next to Save Current Pose.
- Restores only the selected timeline pose from the persistent model recovery history.
- Reloads the selected pose and timeline thumbnail; reports when no earlier version exists.
- Clears unsaved draft flag before reloading to avoid immediately overwriting the restored pose.
- Recovery is persisted with Save Creature; this action itself does not automatically write to disk.
- Existing Windows GUI verification and pixel-depreciation regression checks remain deferred.

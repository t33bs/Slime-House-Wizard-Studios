# Phase 14: history selection and canvas synchronization

Audit: Undo/Redo restored model snapshots and rebuilt timeline thumbnails but did not reliably reapply the selected saved pose to the editing canvas. After structural edits, row indices can also refer to a different pose.

Change: capture the selected pose's stable ID before Undo/Redo; after restoring model history, resolve that ID in the restored animation (or clamp to an existing row if absent), then load the saved pose through the existing timeline selection path. Playback rebase remains conditional on a structural timeline change.

Windows verification deferred: selected row, canvas, preview, deleted-pose fallback, animation playback, and rapid Undo/Redo.

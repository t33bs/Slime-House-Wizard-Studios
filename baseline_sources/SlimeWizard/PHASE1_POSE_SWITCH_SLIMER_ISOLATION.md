# Phase 1 — Slimer selection isolation on timeline pose switches

- When loading a different timeline pose (or animation/project draft key), clear temporary Slimer masks, cached selection source, drag state and transform values **after** applying the destination pose.
- Keep Slimer selected. Do not alter saved pose snapshots or delete layers.
- Refreshing the same pose does not discard its in-progress selection.
- The existing `begin_pose_draft` call preserves edits to the outgoing pose before applying the destination.
- Added two contract tests; full source suite: 179 tests passing in this environment.

## Deferred Windows GUI verification
1. Verify Slimer asset labels match timeline pose numbering, including reordering.
2. Safely migrate older projects with duplicate `Slimer pose` layers.
3. Repeat highlight/drag/Place Frame cycles and compare RGBA pixels.
4. Verify pose recovery and restore across restarts.
5. Highlight on Pose A, switch to Pose B with Slimer active; verify no old selection or pixels appear. Switch back and confirm saved artwork is unchanged.

This patch does not establish that all pixel depreciation causes are resolved. No Windows EXE built or GUI tested.

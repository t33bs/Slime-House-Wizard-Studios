# Phase 15: stale Slimer selection guard

A Slimer selection holds a snapshot of the rendered source. If a pose or layer is edited after the selection was created, committing Move Original from that old snapshot risks erasing the wrong pixels. `_slimer_commit` now checks that the source still matches the current render *before* saving a draft, recording history, erasing any source, or creating a frame. A mismatch leaves the artwork and timeline unchanged and instructs the user to clear and reselect.

This is a defensive fix, **not** a confirmed resolution of the Windows user's reported Move Original rejection. Both previews and the original commit-path issue still require Windows GUI verification. Existing uncommitted GitHub files should not be overwritten without a backup.

# Phase 1 — Empty animation overlay isolation

When switching from an animation with a visible `Slimer pose overlay` to a different animation with no saved poses, the live overlay is hidden. The shared creature base remains available, and previously saved pose snapshots are not changed. Returning to a saved pose restores its own overlay from its snapshot.

This is a source-level safeguard, not a Windows GUI verification. The deferred Windows test list remains applicable.

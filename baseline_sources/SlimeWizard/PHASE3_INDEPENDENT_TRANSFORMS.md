# Original Slimer roadmap — Phase 3

Independent color-phase selection masks already existed, but the transform number controls were shared across phases. Phase switching now saves and restores X/Y, rotation, and scale for each phase independently. Switching suppresses intermediate value-change events so it does not create spurious undo entries. Clear Selection resets the phase transform cache.

Pending Windows GUI verification: phase switching, transform isolation, preview alignment, and interaction with Edit Selection. Phase 4's separate per-color transform tabs are not yet implemented.

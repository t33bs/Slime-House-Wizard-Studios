# Phase 15 — Timeline insertion and legacy recipe menu cleanup

- Renamed Add pose to **Insert pose after selected** to make middle-of-timeline behavior explicit.
- The insertion index is clamped to the current animation's length and uses the model's independent snapshot insertion.
- Removed legacy animation recipe choices from the **+ workspace menu**. Existing Choose Animation dropdown remains intact; Idle is still a valid animation name, not a recipe button.
- Left hidden legacy recipe internals in place until their dependencies can be safely removed.
- No installer testing performed. Windows UI validation pending.

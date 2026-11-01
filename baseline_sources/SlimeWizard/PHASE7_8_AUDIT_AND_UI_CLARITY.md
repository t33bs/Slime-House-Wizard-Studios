# Original roadmap: Phase 7 audit and Phase 8 targeted UI cleanup

Phase 7 is already present: the selected-pixels-only Slimer Preview is in the right Compare & Preview panel, and preview generation is deferred until Finish Selecting. No duplicate preview implementation was made.

Phase 8 targeted cleanup: updated outdated Slimer help text, tooltips and status messages to reflect the implemented color tabs, Finish Selecting / Edit Selection workflow, and Confirm All Placements. No animation engines, placement operations, or pixel buffers were modified.

## Deferred Windows checks
- Slimer Preview stays in the right panel; it does not cover highlighted pixels while painting.
- Slime Buddy instructions match the visible selection workflow, and remain hidden when Slime Buddy is OFF.
- Confirm All Placements and single-selection placement options are clearly distinguishable.
- Verify no tooltips obscure the narrow left panel.

## Next roadmap
Phase 9: audit user-uploaded reference viewer before implementing anything; skip if complete.

# Phase 1: Slime Cleaner and Slimer Preview

Reported by user: Slime Cleaner does not visibly erase/clear pixels; dedicated Slimer Preview is not implemented.

Fix: cleaner_paint now copies modified part images back into model.originals. The renderer uses model.originals via resolved_pose/render_part; previously editing parts alone could leave the displayed canvas unchanged. Existing cleaner engine tests passed, but this integration bug was not covered by them.

Outstanding: Add an explicit Slimer Preview panel displaying only selected pixels, reflecting selection and transforms in real time, distinct from the ordinary full-creature animation preview. Test in actual Windows UI. Restore both Move Original Pixels (default) and Copy Pixels modes, with undo and pose isolation.

# Phase 6 — Move Original foundation

- Enables optional Move Original; Copy remains the default.
- On placement, highlighted source pixels are cleared from visible layers, then the transformed selection is added as a new layer.
- A single main-history snapshot precedes the entire placement, allowing undo/redo of source erasure and layer/frame creation.
- Existing Slimer Undo/Redo, Slime Buddy, and keyboard shortcuts are preserved.

## Known limitations / remaining work

- Move Original clears the selection across all visible layers. In overlapping artwork this can expose transparency rather than automatically reconstructing hidden background pixels.
- Interactive transform handles and the custom slime cursor are not yet implemented.
- Windows GUI validation and installer/portable packaging remain outstanding.

# Phase 9 follow-up — Move Original default and frame PNG round-trip

- Move Original is now checked by default for Slimer; uncheck for Copy.
- Export Frame PNG and Replace Frame PNG are both on the top toolbar (scroll horizontally if needed).
- Replace Frame PNG imports an edited full-canvas transparent PNG as a frame-specific layer; other frames remain unchanged.
- Replacement PNG must match the original creature canvas dimensions. Export a frame first, then edit it in Slime House Studios without changing canvas size.
- Main Undo can revert the replacement; the replacement frame is flattened into a new editable layer (it does not automatically reconstruct individual rig pieces).
- Earlier saved poses remain independently renderable; new imported parts are hidden when loading older frames.
- Windows GUI, GitHub Actions portable and installer builds remain to be tested.

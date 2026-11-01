# Slimer Tool — Phase 2 development snapshot

Built on the Phase 1 source, preserving the existing project and Windows GitHub Actions build workflow.

- Slimer selection mode in the left asset panel; left-drag paints a pixel selection, right-drag erases it.
- Brush size, integer X/Y offset, rotation, and nearest-neighbor scale controls.
- Canvas previews the selection tint and transformed pixels.
- Place as Layer adds only selected transformed pixels as a transparent editable layer.
- Place Frame adds that layer and inserts a new timeline pose as a single undoable transaction.
- Ctrl+Z, Ctrl+Y, Ctrl+Shift+Z use the existing per-project history, including frame and layer state.
- Clear Selection resets the temporary mask and transforms.

**Limitations:** UI could not be smoke-tested here because PySide6 is not installed in this environment. Tests exercise the model and history integration. Mouse-driven drag handles for transforming selected pixels, persistent selection editing history, and Move Original mode are not implemented yet. Move Original is visibly disabled rather than silently misbehaving. No Windows executables or installer were built in this phase.

# Phase 57 — Avoid duplicate full-canvas render on live preview

`refresh()` previously called `model.render()` to draw the editable canvas, then `refresh_preview()` called `model.render(None)` again when there was no saved pose to preview. On large 512×512 and 1024×1024 canvases, that duplicated all layer compositing for every Slimer brush refresh.

`refresh()` now passes the original, unmodified live composite to `refresh_preview()`. The preview reuses it only when no saved pose is selected. Saved animation frames still render their independent pose snapshots; editor-only selection, handles and onion skin never leak into the preview. The optional parameter is type-checked to avoid treating Qt signal arguments as image objects.

Windows/PySide6 GUI responsiveness remains unverified in this headless environment.

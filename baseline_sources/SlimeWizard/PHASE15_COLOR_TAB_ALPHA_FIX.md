# Phase 59 — Color-tab alpha compositing

The legacy multi-color Slimer confirmation path pasted selected layers using a binary nonzero-alpha mask. This incorrectly made semi-transparent source pixels fully opaque. It now uses Pillow's `alpha_composite` for the selected RGBA previews, preserving fractional alpha and correct overlapping color-tab blending. Three image-level regression cases plus one UI wiring test were added. The standard Edit Selection → Apply Move workflow remains unchanged. Windows GUI testing remains outstanding.

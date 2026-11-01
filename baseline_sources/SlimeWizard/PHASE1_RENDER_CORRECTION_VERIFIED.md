# Phase 1 — Verified render alpha correction

Source baseline: local `phase1_project_activation_fix` directory.

## Confirmed defect
`studio/pet_suite_model.py` `render_part()` previously called `layer.paste(part, (x, y), part)`, applying the source alpha as a paste mask and attenuating the alpha before `render()` alpha-composited the layer.

## Correction
Use `layer.paste(part, (x, y))` to copy source RGBA unchanged into the transparent temporary layer; `render()` then performs one alpha composite.

## Tests run
- `python -m unittest discover -s tests -p test_phase1_render_rgba_regression.py -v` — 2 passed.
- `python -m unittest discover -s tests -q` — 185 passed.

## Not verified
Windows GUI interaction, original Slimer repeated-drag pixel depreciation, legacy duplicate-layer migration, and build/release EXE. These remain deferred.

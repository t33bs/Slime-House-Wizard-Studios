# Phase 1 — Animation and step Slimer isolation

- Animation changes discard transient Slimer selection state, including when the destination animation has no poses.
- Step changes compare the project/animation/step key and clear transient selections after loading the destination pose.
- Same-step refresh does not intentionally clear an unfinished selection.
- Saved pose artwork is not deleted by this reset.

Automated verification: `python -m pytest -q` — 191 passed, 433 subtests passed (Linux headless source/model checks). Windows GUI interactions have not been verified.

Deferred Windows tests: timeline Slimer numbering and reordering; safe handling of legacy duplicate Slimer pose layers; repeated highlighting/dragging/Place Frame pixel integrity; recoverable versions of existing timeline poses; animation/step switching with unfinished selections.

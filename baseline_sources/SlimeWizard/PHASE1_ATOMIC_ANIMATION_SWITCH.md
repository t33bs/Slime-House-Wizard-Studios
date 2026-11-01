# Phase 1 — Atomic animation switch

Animation changes now rebuild the step list with Qt row-change signals blocked. Previously, setting the first row could invoke `select_step` while the animation selector was being rebuilt. The destination saved pose is now explicitly loaded after the list is ready, then transient Slimer state is reinitialized against the destination artwork. Empty destination animations clear the previous pose draft key.

Regression coverage: `tests/test_phase1_animation_switch_atomic.py`. These are source-level tests; actual Windows GUI switching and the deferred pixel-depreciation checklist remain unverified.

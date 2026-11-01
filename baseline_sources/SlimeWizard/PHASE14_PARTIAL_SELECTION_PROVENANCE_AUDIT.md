# Phase 14 — Partial selection provenance audit

Added `classify_source_selection` to `studio/pixel_source_mapping.py`.

For each source pixel, it compares all rendered nearest-neighbor occurrences with the selection. A source pixel is classified **complete** only when all visible rendered occurrences are selected; it is **partial** if some but not all are selected. The optional rendered alpha channel excludes invisible occurrences. Dimensions are validated. This helper is read-only and does not bypass existing destructive erase guards.

Four tests cover partial and complete scaled footprints, mixed source pixels, alpha filtering, and invalid dimensions. Headless suite: 298 passed, 1 skipped, 441 subtests passed.

## Remaining before enabling destructive transformed moves
- Verify the mapping and selection policy on inherited rotation/resize, clipping and overlapping layers.
- Resolve pose-specific source buffers, history and shared source pixels safely.
- Validate Windows visual behavior and user messaging.

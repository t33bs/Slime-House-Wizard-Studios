# Phase 1 — Slimer overlay RGBA integrity

Changed repeated Place Frame overlay merging to copy selected RGBA pixels directly into the existing overlay instead of alpha-compositing them. Repeated alpha compositing increases opacity of translucent pixels and is not idempotent; direct replacement preserves their RGBA values. The selected pixel mask is binary (nonzero alpha), so unselected pixels remain untouched. This is a narrow correction, not proof that the user's original pixel-loss issue is fully resolved. Deferred Windows tests remain required.

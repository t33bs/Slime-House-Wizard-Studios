# Phase 54 — per-creature canvas sizes

New creature now offers 64, 128 (default), 256, 512, 1024 square pixel canvases or custom width and height from 1 to 1024 each. Cancel at any prompt creates nothing. Each creature keeps its own canvas size; existing projects are not resized. The existing model and project serialization already support rectangular sizes. No changes to imported artwork, pixel scaling, or existing projects.

The GUI prompt still needs Windows testing. Larger canvases may cost more memory and time for multi-frame editing; this is an initial limit rather than a performance guarantee.

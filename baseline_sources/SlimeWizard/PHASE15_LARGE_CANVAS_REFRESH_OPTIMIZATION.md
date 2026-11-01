# Phase 56 — large canvas refresh optimization

Slime Wizard previously converted the entire rendered canvas to QImage before adding Slimer highlights, then converted the full canvas a second time if Slimer was enabled. This discarded the first QImage and performed redundant RGBA buffer allocation on every brush stroke.

Refresh now creates the final QImage only once after all overlays. This preserves canvas content and selection previews while reducing work for 512×512 and 1024×1024 projects.

A source-level regression test guards against reintroducing the duplicate conversion. Windows GUI interaction and performance still require validation on a machine with PySide6.

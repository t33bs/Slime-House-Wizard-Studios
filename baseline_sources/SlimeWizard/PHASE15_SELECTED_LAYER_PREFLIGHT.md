# Phase 15 — selected-layer source preflight

The layered source-erase planner now checks cached image/source consistency only for visible assets whose rendered alpha overlaps the selection. Unrelated assets with stale pose-local image caches no longer veto a safe selection from another asset. A contributing asset still requires complete provenance checks. Added a two-layer headless regression test.

This does not establish that repeated Windows Slimer Apply Move is fixed. Windows GUI verification remains necessary. Work was performed in an isolated development copy, not the GitHub working tree.

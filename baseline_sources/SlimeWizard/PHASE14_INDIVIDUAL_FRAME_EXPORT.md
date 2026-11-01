# Post-roadmap feature: Export All Frames

Audit finding: Export Frame PNG exported only the selected pose; the primary requirement for all individual pose PNGs plus timing metadata was not met by that control.

Added a separate Export All Frames action, backed by PetSuiteModel.export_individual_frames. It exports one lossless transparent PNG per saved pose, with animation identity, zero-based frame index, and duration_ms in a companion JSON. The existing single-frame export remains available. Animation labels that sanitize to the same filename are disambiguated. Export is read-only with respect to the creature model. Windows UI testing is deferred.

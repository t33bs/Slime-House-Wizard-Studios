# Build 1.8 — Windows CI startup / SHS→Wizard handoff correction

The Windows GitHub Actions Build 1.7 job stopped in `SlimeHouseWizardStudios.__init__`
while connecting `studio.linked_png_saved`: `AttributeError: 'MainWindow' object
has no attribute 'linked_png_saved'`.

- Replace this custom cross-editor Qt signal with an explicit per-instance
  Python completion callback registered by the combined host. Standalone SHS
  has no registered callback and remains a save-only editor.
- Invoke the callback only **after** `safe_export` validates the PNG and
  commits it to disk. The original Wizard pose identity, dimensions, and
  animation checks remain untouched.
- Failed PNG saves do not notify the host or clear SHS dirty state. A failure
  during Wizard return reports `PNG saved; Wizard return failed` correctly.
- Preserve one-shot handoff, tab switching, frame count/IDs and Save Creature.
- Added five no-Qt executable contract tests for success, failed save,
  failed handoff, standalone SHS, and host wiring; the existing Qt GUI
  click-through tests are retained for Windows.

Local integration result: **48 passed, 6 skipped** (the skips need PySide6).
The Windows Actions test run is required to confirm the Qt issue is resolved.

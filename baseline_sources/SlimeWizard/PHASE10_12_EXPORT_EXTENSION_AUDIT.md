# Phases 10–12: targeted export audit (2026-10-28)

Existing features retained: sprite-sheet PNG+JSON export, Save As dialogs, animation-safe name collision handling, GIF and APNG encoders, frame timing, transparency, and non-mutating exports.

Actual gap fixed: APNG outputs were named `.png`; now named `.apng` so users can distinguish animation files from static PNG. The underlying PNG/APNG file format is unchanged, and Pillow explicitly encodes PNG format. The animation export dialog now clarifies that the selected filename is a base name for GIF and APNG outputs.

Automated validation: `python -m pytest -q`: 246 passed, 1 skipped, 433 subtests passed. Windows visual/file-association checks queued separately.

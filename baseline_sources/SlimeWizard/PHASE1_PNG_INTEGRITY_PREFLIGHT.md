# PNG integrity preflight — 2026-10-28

Added `studio/project_png_validation.py` and integrated it after manifest validation and missing-file checks, before project model construction. Checks PNG identity, container structure and complete pixel decoding. Legacy `part_###.png` naming remains supported. The loader rejects damaged artwork with an actionable filename and backup-recovery message, without modifying source files.

Automated checks: 252 passed, 433 subtests passed, 1 GUI-dependent test skipped. Windows UI behavior remains unverified.

# Phase 15 — Legacy recipe UI internals cleanup

Removed obsolete Follow Recipe toggle, hidden recipe step list, hidden instruction label, step-list event hookups and synchronization from friendly_animator.py. Timeline navigation now uses saved poses directly, without the hidden step-list widget. Updated three static tests to assert absence of removed controls while retaining animation and saved-pose isolation contracts.

Validation: `python -m pytest -q` => 348 passed, 8 skipped, 441 subtests passed. `compileall` passed.

Not yet removed: the 31 named animation templates and legacy recipe reference/guidance modules. These remain connected to animation choice, compatibility, bundled-resource checks, and optional motion guidance. Their removal requires a separate migration so existing projects and current reference viewer functionality are not broken. GUI tests skipped due to unavailable PySide6.

# Phase 15: recipe-free project selector isolation

Added tests for two simultaneous independent creature projects, confirming custom animation names do not leak between selectors and neither project is mutated by selector inspection. Added deduplication test for historical labels that also occur in saved animations. This checkpoint builds on the recipe-free UI guardrails.

Validation: `PYTHONPATH=. python -m pytest -q` => 344 passed, 8 skipped, 12 subtests passed. GUI tests remain skipped; no Windows GUI verification. No Slimer or Phase 16 edits. Verified original safety backup is not modified.

Phase 14 Windows pytest hang diagnostics patch

Copy ONLY .github/workflows/build-friendly-animator.yml into the repository root, preserving the .github/workflows path.

Changes: install pytest-timeout, show per-test progress, stop on first failure, print slowest tests, set 120-second per-test timeout and 12-minute job-step timeout. Preserve log artifact on failure. No application source files changed.

Commit and push; inspect the NEW GitHub Actions run. This is diagnostic and does not guarantee Windows tests pass.

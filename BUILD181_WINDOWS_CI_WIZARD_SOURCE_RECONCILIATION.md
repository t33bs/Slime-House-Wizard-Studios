# Build 1.8.1 — Reconcile Wizard file omitted from the GitHub update

## Symptom
The GitHub Actions Build 1.8 Windows integration job failed in
`tests/test_build15_hotkeys_handoff_model.py::test_both_save_buttons_use_one_success_only_return_path`.
The combined host and tests expected an SHS-to-Wizard reload method that checks
stable pose identity, returns explicit success/failure and rejects unfinished edits,
but the committed Wizard `shws_wizard/friendly_animator.py` still contained the
older implementation. In particular, it did not contain the expected pose-ID guard.

## Fix
This patch ships the **complete intended Build 1.8 Wizard file**. Its
`reload_shs_edit` checks the bound project, animation, timeline index, original
stable pose ID, unfinished Slimer edits, PNG format and canvas size; it then
imports into only the target existing pose, reports `True` on success and `False`
on failure. It does not automatically create a new timeline frame.

Build 1.8's earlier callback correction in `main.py` and `studio/app.py` is
**still required**. This is a follow-on synchronization patch, not a replacement
for that earlier update. Do not apply it onto Build 1.7 without Build 1.8.

Added `tests/test_build181_wizard_handoff_runtime.py`: executes the real Wizard
reload method using a small non-Qt harness to verify rejection of a changed
pose ID, rejection of unfinished Slimer work, and a successful import into
exactly one timeline pose while preserving IDs, timing, and other poses.

## Apply with GitHub Desktop
Extract this ZIP and copy its contents to the root of the existing combined
`Slime-House-Wizard-Studios` repository, preserving subfolders. Replace the
Wizard file. Commit as `Build 1.8.1 - Restore Wizard PNG handoff safeguards`
and push. Wait for GitHub Actions. Only apply the separate Build 1.9 APNG patch
**after** this Windows build succeeds.

This patch does not change the APNG exporter, SHS tool hotkeys, or standalone
Slime Buddy. Keep a normal Git backup/commit so the change can be reverted.

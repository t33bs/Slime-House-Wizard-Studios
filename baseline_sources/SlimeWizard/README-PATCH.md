# Phase 103 GitHub Actions fix — Portable Windows build

This ZIP contains **only a GitHub Actions workflow** and this README. It does NOT contain or modify `friendly_animator.py`, any Slime Buddy files, art assets, tests, or prior backups.

## Why the existing workflow failed

Your uploaded Windows log reports `1 failed, 60 passed`, stopping at `tests/test_phase101_center_chrome_boundary.py::test_existing_editor_methods_match_phase100_baseline`. The old workflow uses Python 3.12, while Phase 103's frozen AST hashes match Python 3.13 in the verified project source. AST serialized fingerprints are Python-version-sensitive.

## Apply through GitHub Desktop

1. Open **SLIME-WIZARD** in GitHub Desktop and select **Repository > Show in Explorer**.
2. Make a copy of the existing `.github/workflows/build-friendly-animator.yml` as a backup OUTSIDE the repository.
3. Unzip this patch. Copy the patch's `.github` folder into the **root of the cloned repository**, merging folders and replacing only `.github/workflows/build-friendly-animator.yml`.
4. Verify GitHub Desktop shows **one changed workflow file**. No app source or sprite assets should change.
5. Enter a commit message like `Fix Python baseline and build portable Phase 103`, click **Commit to main**, then **Push origin**.
6. Open GitHub > your `SLIME-WIZARD` repo > **Actions**, select `Slime Wizard Phase 103 - Windows Portable`, and open the new run. Or click **Run workflow** on `main`.
7. On a successful run, open **Summary > Artifacts > SlimeWizard-Phase103-Windows-Portable**, download, extract the Actions artifact, then extract the inner `SlimeWizard-Phase103-Windows-Portable.zip`. Run `SlimeWizard/SlimeWizard.exe`.

This creates a build artifact available from GitHub Actions; it does **not** automatically create or publish a GitHub Release.

## What stays unchanged

- Full approved Phase 103 Slime Wizard application, Slime Buddy and editing tools.
- The repository's current tests; any genuine later test failures still block packaging.
- No installer or uninstall steps: output is a portable ZIP.

## Validation limitations

The YAML and local Python-3.13 method-hash comparison were checked. The actual Windows runner/packaged executable cannot be verified until the GitHub Actions job completes. If another test fails after the Python fix, use the newly uploaded `SlimeWizard-Phase103-Windows-Test-Logs` artifact to diagnose it rather than skipping that test.

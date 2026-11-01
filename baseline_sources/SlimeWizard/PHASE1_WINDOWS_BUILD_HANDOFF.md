# Phase 1 Windows build handoff

The GitHub Actions workflow `.github/workflows/build-friendly-animator.yml` is configured for `workflow_dispatch` on a Windows runner. It compiles the source, runs the full unittest regression suite, packages the portable PyInstaller directory, runs a packaged `--smoke-test`, builds an Inno Setup installer, and tests install/uninstall. It uploads both portable and installer artifacts.

## Newly added release gates

- Run `compileall` before packaging.
- Capture full Windows unittest output as a downloadable Actions artifact even when tests fail.
- Stop packaging if the Windows regression suite fails.
- Fix the upgrade smoke-test failure message so it reports the actual process exit code rather than an unrelated PowerShell exception variable.

## Manual checks deferred until the Windows EXE is available

1. Timeline Slimer Pose numbering after insert/reorder/delete.
2. Legacy duplicate `Slimer pose` layer migration without loss of legitimate artwork.
3. Repeated highlight/drag/Place Frame operations with pixel-exact export comparisons.
4. Restore Previous Pose after save/reopen/reorder/delete.
5. Semi-transparent pixel integrity through editing and export.

The workflow is prepared but has **not** been executed on a Windows runner in this environment. Its smoke test is not a substitute for real mouse interactions. No GUI test has been claimed as passing.

Phase 14 Windows asset cleanup path comparison patch

Copy the contents of this ZIP into the ROOT of the Slime-House-Friendly-Animator repository, merging the studio/ and tests/ folders. Only two existing files are replaced:
 studio/asset_versions.py
 tests/test_asset_versions.py

Root cause hypothesis: on Windows Path.resolve() can expand a short 8.3 parent name such as RUNNER~1. The cleanup preflight previously compared the initial active path against a freshly inspected path with different lexical spelling, aborting even though both pointed to the same folder. This patch compares canonical resolved paths, preserving the safety check if the active directory actually changes.

Verified in Linux environment: 213 unittest tests OK (1 skipped); pytest 327 passed, 1 skipped, 441 subtests. Windows CI verification remains pending.

Commit and push to main, then inspect the NEW GitHub Actions run. Do not bypass regression tests.

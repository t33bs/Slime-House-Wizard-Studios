# Phase 1: Duplicate Pose identity safeguard

The GUI Duplicate Pose action now calls `PetSuiteModel.insert_frame` instead of directly appending to `animations`. This keeps stable pose IDs and frame durations synchronized, preserves existing recovery histories, and loads the new independent snapshot using the normal timeline selection path.

Two new regression tests cover model pose/recovery isolation and the GUI source call path. `python -m unittest discover -s tests -q` passed: 177 tests.

Windows GUI validation and the previously deferred manual checks remain pending. This patch does not establish that the original Slimer pixel-loss bug is resolved.

# SHWS Build 1.4 — Slimer layer reselection / transparent click fix

**Reported bug:** Make Move 1 with Slimer and Apply Move; make Move 2 and Apply Move; attempt to reposition Move 1 from the Asset Library. Clicking the first move's artwork could silently select and drag Move 2 instead.

**Verified code cause:** `DragCanvas.mousePressEvent` iterated newest-first and hit-tested the `x/y + image.width/height` rectangle. A Slimer move stores a 128×128 full-canvas PNG, even when it contains only a handful of opaque pixels. Thus every new move obscured almost the entire click surface of earlier moves, regardless of alpha.

**Correction:** Add `shws_wizard/studio/asset_hit_test.py` as a pure isolated selection policy. When clicking without an unconfirmed move, test the selected layer's rendered nonzero alpha first; otherwise choose the topmost visible pixel. Tests evaluate alpha using the *actual Wizard model render_part* so transforms, rotations and rig attachment offsets remain accurate. Existing staged-edit safety remains: only the unconfirmed destination can be dragged before Apply/Cancel. No alteration to frame/export/asset data structures, alpha compositing, or Move Original erase rules.

## User acceptance on Windows

1. In Wizard, import a sprite with two separate visible sections. Activate Slimer; highlight first section; Edit Selection; reposition it; Apply Move.
2. Highlight a *different* section; Edit Selection; reposition it; Apply Move.
3. In the Asset Library select **Slimer Layer 001**; click **Edit Selection** if handles are not visible. Click and drag its visible artwork. The selected layer should remain Layer 001, and its X/Y should change. Layer 002 X/Y should NOT change.
4. Repeat for **Slimer Layer 002**; it must still reposition normally. Try selecting Layer 001 in the transform menu. Try moving the two assets into overlapping positions, then selecting each in the library and moving again.
5. Click empty transparent canvas space: it must not select a Slimer layer simply because its full-canvas PNG overlaps that point.
6. Make a third unconfirmed edit: selecting earlier assets must remain blocked until Apply Move or Cancel.
7. Place 7+ poses, save/reopen `.rig.json`, and export GIF/PNG; older saved poses and unselected layers must not change.

**Regression checks from the repository root:**

```powershell
py -3.13 -m pytest tests/test_build14_slimer_layer_hit_test.py tests/test_build14_slimer_layer_reselect_gui.py -q
py -3.13 -m pytest tests -q
```

**Local environment:** No PySide6 is installed in the execution environment, and dependency download was unavailable. Python model/selection tests execute locally; Qt mouse acceptance is provided for Windows GitHub Actions and manual checking. A green local model test is not a claim of verified mouse behavior on the Windows application.

**Safety/provenance:** Base is SHWS Build 1.3. All original SHS and Wizard source copies under baseline_sources remain unchanged. The helper is new; changed production files are friendly_animator.py, main.py, packaging/SHWS.iss and the GitHub Actions build naming. Existing SHS studio files and Slimer editing algorithms remain untouched.

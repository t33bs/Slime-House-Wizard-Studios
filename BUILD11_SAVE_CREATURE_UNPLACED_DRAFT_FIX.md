# SHWS Build 1.1 — Save Creature before Place Frame

**Base:** recovered `SLIME-HOUSE-WIZARD-STUDIOS-Build1-Source.zip` plus the **later approved** `SHWS-Installer-Fix-FRESH-2026-11-01.zip` installer path correction. The untouched original SHS and Slime Wizard source trees remain under `baseline_sources/` for independent regression validation. No changes to Slime Buddy standalone project.

## Problem

The Wizard `save_project_by_id()` explicitly returned `False` while `_next_pose_capture_pending=True`. Users could not save an editable `.rig.json` creature until they placed the next timeline pose. That safeguard prevented an overwrite of the previously saved pose but also prevented backing up unfinished next-pose edits.

## Resolution

- **Save Creature works while the NEXT pose is still a draft.** It records its stable owning pose ID and animation as `unplaced_next_pose` in the `.rig.json` manifest. All editable live artwork remains in the existing top-level `parts` and original PNG asset store.
- The older saved animation poses stay in `animations` and **are not edited, duplicated or implicitly placed** by Save Creature.
- Loading this saved project in Build 1.1 automatically restores the unfinished next-pose canvas **without applying the saved pose over it**. The user can make more edits and later explicitly click Place Frame to capture the new pose, or intentionally select Save Current Pose to replace the old one.
- Switching creature tabs preserves the draft's ownership and editable canvas. Clicking the selected timeline thumbnail no longer silently discards the unfinished work.
- An unconfirmed temporary Slimer layer still requires Apply Move or Cancel Unconfirmed Layer before saving. This protects source erasure integrity.
- Project JSON input validation rejects an invalid/mismatched draft pose ID before opening the project. The unsaved-draft state participates in the project fingerprint.
- All pre-existing standalone editor source baselines remain included and unchanged.
- Preserves the installer icon/source/output path fix (`..\\`) from November 1.

## Local verification

- `python -m compileall -q main.py studio shws_wizard tests`: PASS
- `python -m pytest tests -q`: **16 passed, 1 skipped** (GUI Qt test skipped because PySide6 isn't available in this Linux test environment)
- New PNG/JSON roundtrip tests at 1, 6, 7, and 12 existing poses compare exact RGBA frame content, IDs, draft pixels, and unchanged earlier saved frames.
- Windows GitHub Actions runs the Qt GUI regression in `tests/test_build11_unplaced_next_pose_gui.py` before packaging. **A passing Windows run is still required.**

## Windows acceptance (source checkout, before release)

1. Keep a backup of the original project. Install dependencies from `requirements.txt` and `pytest`, then run `python -m pytest tests -q` in the SHWS repository. Ensure the Build 1.1 Qt GUI test runs, not skips.
2. Launch unified SHWS (`python main.py`) and enter **Slime Wizard**. Open or create a creature.
3. Create at least 7 placed, visually different poses. With the last pose selected, perform a new Slimer edit and **Apply Move**. **Do not Place Frame.**
4. Click **Save creature** and save to `.rig.json`. Confirm the success status reports an unfinished draft, no new timeline thumbnail was created, and the already-saved poses remain different.
5. Close and reopen the project from that JSON. Confirm the still-unplaced edit is visible and editable. Click its existing thumbnail; it must not erase the draft. Only then click **Place Frame**, and verify one additional new pose appears while all old pose previews stay unchanged.
6. Confirm export PNG / GIF / APNG and Save Current Pose continue to behave as designed.

## Applying this change to GitHub

Use the small overlay archive if your repo is based on the same Build 1 source. Extract it over the repository root, review only the changed files, commit and push; GitHub Actions should build the Windows portable application and optional installer. For a different or newer source branch, compare changes instead of blindly overwriting.

**Limitation:** This resolves the direct Save Creature blocker and adds project draft restoration. The separately reported Windows visual/timeline problem after Frame 6 still needs a user project and Windows GUI reproduction; the model's isolated 12-frame test does not prove that other issue resolved.

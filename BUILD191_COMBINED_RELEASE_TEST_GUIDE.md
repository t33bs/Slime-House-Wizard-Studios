# Build 1.9.1 — combined Windows candidate

Included in one source tree:

1. Build 1.8.1 handoff/source reconciliation.
2. Build 1.8.2 always-visible SHS **Send to Slime Wizard as New Pose**, inserting a new, independent frame (not overwriting previous poses).
3. Build 1.9 APNG full-canvas SOURCE blend, decoded RGBA and timing validation before atomic replacement; optional non-destructive detached-pixel warnings.

Apply the **Build 1.9.1 Combined Update Patch** onto a repository that already has 1.8.1 (or later) and do not apply the old Build 1.9 patch afterward. The combined full source archive is an alternative for a fresh repository, not a reason to overwrite your live project files. Never commit or share your own creature rig artwork in the source repository.

### Local tests

`python -m pytest tests -q`

### Windows acceptance

- Open SHS as its own tab: click **Send to Slime Wizard as New Pose**, verify new timeline frame and unique pose ID; save/reopen rig.
- From Wizard, use **Edit Frame in SHS** and **Save Back to Animator + Return to Wizard**; verify only original pose replaced.
- Export 9-frame 128×128 transparent APNG: reopen with Pillow and compare every RGBA frame to Wizard renders; check frame count, timing and loop.
- Export GIF and sprite sheet to ensure unchanged paths; if detached pixels are reported confirm the popup does not alter pixels or prevent export.
- Verify installer and portable build from GitHub Actions; the host cannot run PySide6/Windows locally.

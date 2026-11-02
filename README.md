# SLIME HOUSE WIZARD STUDIOS — Build 1.9.3

**One Windows application, two native editing workspaces.** This is an **integration candidate**, not a certified release until the Windows GitHub Actions tests and user acceptance tests pass.

## What is integrated

- **SHS Studio**: the complete Slime House Studios PySide6 editor with narrowly scoped approved drawing, saving and handoff fixes.
- **Slime Wizard**: the complete Phase 103+ Wizard editor as a second live Qt tab. To prevent `studio.*` import collisions, its own library is namespaced under `shws_wizard.studio`.
- **Edit Frame in SHS**: Wizard sends the selected saved pose as a temporary PNG to the SHS tab instead of launching a second process. SHS's **Save Back to Animator + Return to Wizard** button now saves the edited PNG, reimports into the *original* saved Wizard timeline pose, and automatically switches back to Wizard **only after successful validation**. The top **Save SHS Pose + Return to Wizard** toolbar button does exactly the same thing. The original pose remains editable, with no new timeline frame.
- **Projects stay independent**. SHS project save format and Wizard creature/pose save format are NOT merged. No destructive format migration is attempted.
- **Slime Buddy**: the Wizard's existing visual helper/guidance remains. The **separate experimental Slime Buddy generator/AI engine is NOT integrated**.

## Windows launch from source

Install Python **3.13**, then in a terminal from the project root:

```powershell
py -3.13 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe main.py
```

For a GUI startup smoke test:

```powershell
.\.venv\Scripts\python.exe main.py --smoke-test
```

This source ZIP is meant to be uploaded as the contents of a **new independent GitHub repository** named `SLIME-HOUSE-WIZARD-STUDIOS` (not nested beneath either original project). The Actions workflow builds **both** a portable application ZIP and an optional Windows setup EXE with an Inno Setup uninstaller.

## GitHub portable build and installer

1. Create the new `SLIME-HOUSE-WIZARD-STUDIOS` repository.
2. Extract this ZIP into a **fresh folder**, then commit and push the folder's *contents*. Do not upload the ZIP itself and do not overwrite the old repositories.
3. Open GitHub **Actions → SHWS Build 1.9.3 - Windows portable and optional installer**.
4. Wait for Windows test/smoke validation. **A green run is required** before sharing an EXE.
5. Download **SLIME-HOUSE-WIZARD-STUDIOS-Build193-Portable-Windows** or **SLIME-HOUSE-WIZARD-STUDIOS-Build193-Installer-Windows** from the successful run's Artifacts.

The portable ZIP runs without installation once extracted. The optional installer creates Start Menu shortcuts and an optional desktop shortcut. **Uninstall removes app files and shortcuts, not saved user projects in home directories.**

## What we have NOT verified in the non-Windows environment

PySide6 is not installed here and package downloads are unavailable, so **no actual Qt startup, mouse UI interaction, Win32 PyInstaller build, or installer uninstall test was executed locally**. The new GitHub workflow is prepared to perform those checks on Windows. The original SHS and Wizard regression sources are copied unchanged into `baseline_sources` for separate regression runs.

## Manual acceptance checks before calling this stable

- SHS opens; draw/import/save/reopen a project without affecting Wizard.
- Wizard opens; edit two different poses with Slimer; Place Frame, reorder timeline, and save/reopen without pose overwrite.
- Use **Edit Frame in SHS** on a saved Wizard pose, draw in SHS, then click the SHS-side **Save Back to Animator + Return to Wizard** button. It must return to Wizard and replace **only** the original pose, without adding another frame. Verify Undo and the earlier frame's source preservation. Test the top toolbar action as well.
- In SHS, try editing a dirty open project then initiate handoff; it must refuse to discard unsaved work.
- Export GIF and APNG/animated PNG from Wizard; check animation timing and transparent pixels in Brave and image preview apps.
- Switch tabs repeatedly while using shortcuts, tools, palettes, docks, preview play/pause, opening dialogs, and saved geometry.
- Test both portable ZIP and optional setup installation followed by uninstall. Verify projects are retained.

## Architecture and source provenance

`main.py` is the sole new launcher. `studio/` retains SHS's editor with narrowly scoped drawing shortcut/save handoff additions. `shws_wizard/` holds Wizard's original source logic with namespace changes and a one-method embedded timeline parent safety adaptation. `baseline_sources/` retains each supplied source snapshot separately for regression testing. SHS and Wizard save settings under their original independent namespaces. `packaging/SHWS.iss` is the new optional installer recipe.

No automatically published GitHub Release, no repository creation, and no remote push occur from this ZIP. The user retains control of their GitHub repositories.

## Licensing and distribution caution

The supplied SHS source snapshot includes an MIT `LICENSE` file. The supplied Slime Wizard source snapshot has no `LICENSE` file at repository root. This integration candidate retains the original SHS license within `baseline_sources/SHS/` and **does not automatically assign a license to the combined project**. Before making the new repo public, confirm the rights and license terms you intend for the Wizard code and the unified product.

The packaged EXE and installer may be unsigned, depending on the GitHub workflow configuration; Windows SmartScreen can show warnings for unsigned downloads.

## Build 1.4 Slimer layer reselection fix

When there are two or more confirmed Slimer edit layers, choose the **first layer**
in the Asset Library (or the canvas Transform layer dropdown), then click
**Edit Selection** to show handles. Clicking its **visible pixels** will now
move that selected layer, not silently jump back to the newest Slimer layer.
Transparent pixels in a padded 128×128 Slimer PNG do not claim clicks.

A pending **unconfirmed** Slimer move still locks editing to that staged layer
until **Apply Move** or **Cancel**. This fix changes mouse selection only; it
does not alter pixel extraction/erasure, timeline ownership, saving, or export.
See `BUILD14_SLIMER_LAYER_RESELECTION_FIX.md` for test instructions.

## Build 1.5 keyboard and SHS→Wizard one-click roundtrip

- **P** = Pencil (or its matching Frame Pencil / Mask Brush context).
- **B** = Paint Bucket. Pencil no longer owns B.
- **E** = Eraser and **I** = Eyedropper.
- From Slime Wizard, select a *saved* pose and click **Edit Frame in SHS**.
- Paint in SHS, then click **Save Back to Animator + Return to Wizard** within SHS (the top toolbar return button also works).
- The app exports the temporary PNG, validates the original project, animation, pose identity, and 128×128 canvas size (or original canvas size), imports an editable full-canvas PNG layer into that *same* saved pose, refreshes the timeline thumbnail and switches to the Wizard tab. Other frames and durations stay unchanged. This is not an automatic save of the `.rig.json`; use **Save Creature** afterward.
- If PNG saving fails, or the intended original pose is no longer selected or was reordered, the editor **does not** import into the wrong pose or switch tabs. The SHS work remains available.
- Undo in Wizard can reverse the imported frame. Standalone SHS behavior is unchanged; the completion signal is only consumed by the unified app.

Tests: `python -m pytest tests -q` plus Windows GUI tests in
`tests/test_build15_hotkeys_handoff_gui.py`. See `BUILD15_HOTKEYS_PNG_HANDOFF.md`.

## Build 1.6 Eyedropper → Pencil default

- A successful **I / Eyedropper** sample returns to **Pencil**, even when the last tool was **Chameleon (2×2)**, Bucket, Eraser, Move or a contextual drawing tool.
- Transparent pixels do not pick a color; Eyedropper stays active until a visible pixel is sampled.
- Existing Chameleon samples remain available if you deliberately select Chameleon later, but Eyedropper will never activate it as a side effect.
- **P = Pencil, B = Paint Bucket, I = Eyedropper, E = Eraser** are unchanged.
- New regression coverage: `tests/test_build16_eyedropper_pencil_model.py` and `tests/test_build16_eyedropper_pencil_gui.py`.
- See `BUILD16_EYEDROPPER_PENCIL_FIX.md` for the exact Windows acceptance sequence.


## Build 1.7 — idle hover bubble / empty dialogue popup

Build 1.3 replaced a problematic custom SHS cursor, but that did not stop
the separate Qt hover-tooltip popup. The combined app now suppresses
ToolTip events **only on the two artwork canvases** and clears any lingering
hover tooltip when entering a canvas or switching editor tabs. The Slime
Wizard transform panel, drawing-tool controls, help tooltips and optional
Slime Buddy dialogue remain intact. No image data or pose save paths change.

Windows acceptance: leave the mouse stationary over blank and painted
portions of the SHS canvas and Slime Wizard canvas; no floating blank box
should appear. Then hover over a real tool/help button and confirm its
normal description still appears. If a box persists, take a screenshot
including the cursor and full app panel so its true widget can be identified.


## Build 1.9.2 release candidate

See `BUILD18_WINDOWS_CI_HANDOFF_FIX.md` for the GitHub Actions startup handoff fix.


## Build 1.9.2 — SHS New Pose + Pixel-Exact APNG Combined

This merge deliberately preserves Build 1.8.2's **Send to Slime Wizard as New Pose** visible SHS button and the earlier linked **Save Back to Animator + Return to Wizard** workflow, plus Build 1.9's verified APNG output and optional (non-destructive) disconnected pixel warnings. Do not apply the older standalone Build 1.9 patch afterward, because that patch contains older `main.py` and `shws_wizard/friendly_animator.py` versions that would remove the new-pose button.

See `BUILD182_SEND_SHS_NEW_WIZARD_POSE.md` and `BUILD19_APNG_FRAME_VERIFICATION.md`. GitHub Actions and Windows GUI verification are required before considering this production ready.


## Build 1.9.2 — SHS reference viewer + Chameleon activation

The SHS left sidebar now has **🖼 Open PNG Reference Window** directly below **Open Intermediate Studio**. It opens a right-side dock with multiple independent PNG references, thumbnail/name selection, a nearest-neighbor zoomable and scrollable preview, transparency checkerboard, hide/show and remove. Reference pixels never enter the drawing canvas, saved `.json` projects, Wizard poses, or animation exports. The viewer is session-only and doesn't modify source files.

Chameleon now automatically discards its held 2×2 pattern **each time you reselect it** after using another tool. Its first click must sample anew; later clicks stamp. **Chameleon: Resample 2×2** remains available. Eyedropper still returns to Pencil. See `BUILD192_SHS_PNG_REFERENCES_CHAMELEON_RESET.md` for Windows tests.

## Build 1.9.3 — Reference sampling (SHS only)

SHS's right-side PNG Reference Window is now an active **read-only sampling surface**.
With **I / Eyedropper** active, click a visible reference pixel to pick its native
RGBA color and return automatically to **Pencil**. With **Chameleon (2×2)** active,
click a full 2×2 native reference block to hold that exact RGBA pattern; clicking
on the main SHS canvas stamps it. Clicking a different reference block while
Chameleon is active explicitly re-samples the pattern. Transparent pixels and
preview checkerboard are never confused. The reference image stays unchanged
and the previously approved Chameleon re-activation reset is preserved.

See `BUILD193_REFERENCE_EYEDROPPER_CHAMELEON.md` for exact usage and
Windows acceptance tests.

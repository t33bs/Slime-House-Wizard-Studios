# SLIME HOUSE WIZARD STUDIOS — Build 1

**One Windows application, two native editing workspaces.** This is an **integration candidate**, not a certified release until the Windows GitHub Actions tests and user acceptance tests pass.

## What is integrated

- **SHS Studio**: the complete Slime House Studios PySide6 editor, carried over without modifying its Python files.
- **Slime Wizard**: the complete Phase 103+ Wizard editor as a second live Qt tab. To prevent `studio.*` import collisions, its own library is namespaced under `shws_wizard.studio`.
- **Edit Frame in SHS**: Wizard sends the selected saved pose as a temporary PNG to the SHS tab instead of launching a second process. SHS's existing **Save Back to Animator PNG** action and Wizard's existing **Reload SHS Edit** continue to work. The host additionally provides **Save SHS PNG + Reload Wizard Pose** while a linked frame is open.
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
3. Open GitHub **Actions → SHWS Build 1.4 - Windows portable and optional installer**.
4. Wait for Windows test/smoke validation. **A green run is required** before sharing an EXE.
5. Download **SLIME-HOUSE-WIZARD-STUDIOS-Build14-Portable-Windows** or **SLIME-HOUSE-WIZARD-STUDIOS-Build14-Installer-Windows** from the successful run's Artifacts.

The portable ZIP runs without installation once extracted. The optional installer creates Start Menu shortcuts and an optional desktop shortcut. **Uninstall removes app files and shortcuts, not saved user projects in home directories.**

## What we have NOT verified in the non-Windows environment

PySide6 is not installed here and package downloads are unavailable, so **no actual Qt startup, mouse UI interaction, Win32 PyInstaller build, or installer uninstall test was executed locally**. The new GitHub workflow is prepared to perform those checks on Windows. The original SHS and Wizard regression sources are copied unchanged into `baseline_sources` for separate regression runs.

## Manual acceptance checks before calling this stable

- SHS opens; draw/import/save/reopen a project without affecting Wizard.
- Wizard opens; edit two different poses with Slimer; Place Frame, reorder timeline, and save/reopen without pose overwrite.
- Use the **Edit Frame in SHS** button on a saved Wizard pose, draw on SHS, save the linked PNG, then reload the correct Wizard pose; verify Undo and original source preservation.
- In SHS, try editing a dirty open project then initiate handoff; it must refuse to discard unsaved work.
- Export GIF and APNG/animated PNG from Wizard; check animation timing and transparent pixels in Brave and image preview apps.
- Switch tabs repeatedly while using shortcuts, tools, palettes, docks, preview play/pause, opening dialogs, and saved geometry.
- Test both portable ZIP and optional setup installation followed by uninstall. Verify projects are retained.

## Architecture and source provenance

`main.py` is the sole new launcher. `studio/` is SHS's unmodified editor library. `shws_wizard/` holds Wizard's original source logic with namespace changes and a one-method embedded timeline parent safety adaptation. `baseline_sources/` retains each supplied source snapshot separately for regression testing. SHS and Wizard save settings under their original independent namespaces. `packaging/SHWS.iss` is the new optional installer recipe.

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

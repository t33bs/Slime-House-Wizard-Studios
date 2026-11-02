# Build 1.9.3 — Sample PNG references with SHS Eyedropper or Chameleon

This is a small additive update based on the complete **Build 1.9.2** combined-app source. **Only SHS** is changed. Slime Wizard's reference-free workflow, save/pose model, APNG exporter, and both SHS→Wizard transfer actions remain untouched.

## Workflow

1. In **SHS**, click **Open PNG Reference Window** beneath **Open Intermediate Studio**, then add one or more PNGs. The right-side reference dock is resizable/closable and retains its list for this app session.
2. **Eyedropper:** Press **I**, click any *visible* native pixel in a reference (not the surrounding checkerboard). Its exact RGBA color becomes the brush color and the active tool changes to **Pencil**. Click the **SHS artwork canvas** to paint. Transparent reference pixels do not change color and keep Eyedropper active.
3. **Chameleon (2×2):** Choose the tool (a new activation always clears its old sample), then click the *top-left* pixel of a complete 2×2 region within the reference. The sampled pattern retains its exact four RGBA pixel values, including transparency. Click the **SHS artwork canvas** to stamp into the selected writable layer. Clicking another valid spot on the reference while Chameleon is still active explicitly **re-samples** the pattern instead of stamping on the reference.
4. **Chameleon: Resample 2×2** still clears the held sample. If you switch tools and later re-activate Chameleon, the held sample is cleared as before.
5. Zooming, scrolling, panel letterboxing, or capped maximum preview resolution do not change sampled source coordinates; clicks are mapped from the actual displayed pixmap back to native image coordinates. Clicking outside the displayed image or attempting a 2×2 sample at the right/bottom edge is safely ignored.

**Important:** The reference file and read-only reference image are never painted, mutated, overwritten, imported as layers, included in project data, or included in animation exports. Reference sampling does not change the sprite or create an undo entry; actual Chameleon stamping on the artwork remains separately undoable.

## Test results / constraints

- `tests/test_build193_reference_sampling_model.py` — exact source/preview mapping, transparency, safe failures, 2×2 alpha preservation, source image immutability, brush color, and tool transitions. Runs without Qt.
- `tests/test_build193_reference_sampling_gui.py` — Windows Qt offscreen mouse events on the real preview label: Eyedropper and Chameleon flows, correct sampling with centered zoom, undo state, actual canvas stamp, and original reference PNG unchanged. **Must be verified on GitHub Actions Windows.**
- Existing Build 1.9.2 tests and integration boundary protection remain.

## Windows acceptance checklist

1. Load a PNG in the reference window and activate **I**. Click a colored pixel. Confirm **Pencil** activates, color matches the reference (including partial opacity), and the artwork does not change until you draw on the canvas.
2. Activate **I** again and click a transparent pixel: Eyedropper should remain active, no checkerboard color should be picked.
3. Activate **Chameleon (2×2)**. Click a 2×2 pattern in the reference. Click on a selected editable SHS artwork layer to stamp. Compare the four destination pixels against the original reference PNG, including transparent pixels.
4. While Chameleon remains active, click another source spot in the reference: this should **replace the held sample**, not change the reference. Test a click too near the image's right/bottom border: no invalid stamp or crash.
5. Change reference zoom, scroll the preview, close/reopen the dock, and repeat. Confirm exact samples follow clicks, and neither the reference file nor other animation poses are modified.
6. Switch away from Chameleon and re-activate it: it must require a fresh sample. Verify the SHS→Wizard **Save Back** and **New Pose** buttons still work, and APNG exports still decode pixel-perfect.

**No Windows EXE/installer or Qt GUI verification is claimed from this Linux/local source test environment.**

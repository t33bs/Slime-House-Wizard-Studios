# Slime Wizard — Phase 76: X / Y / Rotate per Asset Library layer

The Edit Selection button remains the only transition from highlighting into creating a movable layer. No Finish Selecting button is reintroduced.

After selecting artwork and clicking Edit Selection, the created Asset Library layer is selected automatically. Three visual controls appear around its **actual artwork**, not the transparent canvas padding:

- Yellow **X**: drag to move left/right only.
- Green **Y**: drag to move up/down only.
- Blue **R**: drag to rotate around the layer's joint/pivot.

The existing exact-degree control in the Asset Library continues to work. Dragging the artwork normally still permits free X/Y movement. The three handles are drawn as UI overlays in widget coordinates and are never included in PNG/GIF/APNG or project art.

**Edit Selection toggles the handles ON/OFF** when an existing layer is selected. Repeat clicks on a staged layer do not create another layer. The Asset Library row and green 'Selected layer: ... Handles ON/OFF' label identify which layer is active. After Apply Move or Cancel, the temporary handles close and Slimer can highlight again. Once a staged layer has been confirmed, another Asset Library layer can be selected and edited. While a staged Move Original layer is unconfirmed, switching to another layer is blocked to protect the source snapshot.

Move Original Pixels is still ON by default, source erasure happens only after successful Apply Move, Copy Pixels remains supported, and neither the new handles nor their toggling creates animation frames.

## Windows test

From the extracted Phase 76 source directory, with the existing PySide6 venv:

```powershell
& "$env:USERPROFILE\Downloads\DocumentsSlime-Wizard-Pre-Merge-Backup\.venv\Scripts\python.exe" -m pytest -q tests/test_phase76_asset_handles_gui.py tests/test_phase75_staged_rotation_gui.py tests/test_phase74_one_button_edit_selection_gui.py
```

Then launch `friendly_animator.py` with the same python.exe, test X, Y and R manually on real sprite artwork and confirm Apply Move preserves/erases originals as configured.

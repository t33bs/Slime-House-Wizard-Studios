# SHS application picker (Phase 11 follow-up)

- **Set SHS Location** lets users select the actual Slime House Studios `.exe` (installed or portable).
- The path is saved in `QSettings` as `shs_executable` and reused on subsequent edits.
- If the EXE is moved or deleted, Friendly Animator asks the user to locate it again.
- **Edit Frame in SHS** exports the current pose to a temporary transparent PNG and launches the selected EXE with the PNG path as its command-line argument.
- **Reload SHS Edit** reloads that PNG into the original pose only.

**Integration limitation:** The supplied Slime House Studios source does not yet show a startup handler for opening a PNG command-line argument. Until SHS supports this, the app may launch without loading the frame automatically. This source ZIP modifies Friendly Animator only.

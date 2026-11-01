# Missing artwork recovery diagnostics

Project loading now preflights expected PNG files before constructing an editor model.
When files are missing, a readable exception identifies the folder and missing filenames,
explains that the original project was not modified, and recommends restoring a complete
backup. No automatic asset substitution, destructive overwrite, or cleanup occurs.
This is a safety diagnostic, not a full recovery wizard. Windows visual checks remain queued.

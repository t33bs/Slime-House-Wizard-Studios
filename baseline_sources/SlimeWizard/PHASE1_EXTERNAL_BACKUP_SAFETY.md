# External backup safeguards

Asset-version cleanup now fails closed unless the caller explicitly confirms deletion AND asserts that a complete inventory of backup locations has been supplied. The cleanup scanner recursively checks project-directory and supplied backup roots for JSON manifests referencing old asset versions. Missing backup roots, unreadable JSON, and symlinked JSON block deletion. The active manifest is checked again before removal. No cleanup UI or automatic deletion is enabled.

Caveat: the inventory-complete assertion is a responsibility of the caller; arbitrary unknown external backups cannot be discovered automatically. Windows test queue: inspect real backup/recovery paths and determine retention policy before exposing deletion.

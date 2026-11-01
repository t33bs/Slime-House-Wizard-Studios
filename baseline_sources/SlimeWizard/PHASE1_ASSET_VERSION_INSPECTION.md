# Asset-version inspection and opt-in cleanup groundwork

Added studio/asset_versions.py with inspect_asset_versions and cleanup_asset_versions. Inspection is read-only; cleanup requires confirmed=True and is not connected to the GUI. Only same-project, UUID-formatted version folders can be candidates, and same-directory JSON manifests protect referenced folders. Legacy projects disable cleanup. Three new tests cover safety and reference preservation.

Important limitation: external backup/recovery manifests outside the project directory are not scanned. Do not expose deletion in the UI until recovery references and user confirmation have been designed and tested. Windows GUI testing remains deferred.

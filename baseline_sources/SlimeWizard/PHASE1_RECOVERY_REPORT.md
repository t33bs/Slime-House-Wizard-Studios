# Read-only recovery report

`studio.asset_versions.report_asset_recovery(project_path, backup_roots=())` inventories the active version, local older versions, missing versions referenced by known JSON backup manifests, and per-version PNG counts. It warns about unavailable backup locations and unreadable manifests. It does not change any files and does not claim a complete inventory of unknown backups.

Windows testing: validate report against real saved projects and recovery folders, especially missing asset versions and unreadable manifests. No destructive cleanup UI is enabled.

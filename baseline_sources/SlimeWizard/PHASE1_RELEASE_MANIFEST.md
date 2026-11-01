# Phase 1 release manifest safeguard

The Windows CI workflow verifies that the portable executable exists and exactly one installer is produced. It records SHA-256 checksums for both and uploads `phase1-release-sha256.txt` as a separate build artifact. This is a build-output integrity check, not a digital signature and not evidence of GUI pixel integrity.

The Windows runner has not been executed in this environment. The release manifest step must be verified on the next GitHub Actions Windows run.

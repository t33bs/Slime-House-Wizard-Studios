# Original source snapshot manifest

These are the two ZIP files uploaded for the new, separate SHWS Build 1. Their original trees are retained under `baseline_sources/`.

| Input file | SHA-256 | Entries |
|---|---|---:|
| `Slime-house-Studios-main.zip` | `032ed258da59b99c270ceb93dcc372d4a4f05499db6fdc56f41dac2399534157` | 134 |
| `SLIME-WIZARD-main.zip` | `4d33c2df8ff4211a84305cc0e844491144489f12a6926f2ebe24e9fab6355ced` | 556 |

The SHA-256 hashes identify the exact user-supplied baselines and enable a future rollback or provenance audit. The original input ZIPs are not modified.

Local checks: Python AST/compilation passed for both runtime packages; 8 integration/model boundary tests passed. PySide6/Windows GUI, PyInstaller, optional setup, and uninstall are unverified locally and must be checked by GitHub Actions on Windows.

# Slime Wizard Phase 15 — remote source checkpoint

## Changes applied
- Force the right-hand comparison panel visible at startup so the Slimer and animation previews can be found even when older settings hid them.
- Clarify the Move Original source-erase rejection, explicitly saying no frame was placed and artwork was unchanged.
- Preserve both Move Original and Copy Pixels options, and all destructive source-safety checks.

## Verification
- Python compilation passed.
- Linux non-GUI suite: 340 passed, 4 skipped, 441 subtests passed.
- GUI tests are skipped here because PySide6 is unavailable.

## Still unresolved
- Root cause of source/selection rejection on user's Windows artwork.
- Confirm that Apply Move clears selection and Place Frame works in that actual project.
- Visually verify both previews on Windows.

Do not replace your uncommitted GitHub working tree without backing it up. Do not commit this as a fully verified Phase 15 release.

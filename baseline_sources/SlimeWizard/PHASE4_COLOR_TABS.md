# Phase 4: Slimer selection color tabs

Replaced the highlight-phase dropdown with horizontally scrollable, named selection tabs. The existing independent mask and X/Y/rotation/scale state remains unchanged. Adding a new selection adds a tab and selects it. The tab interface preserves the previous picker methods for existing callers.

## Windows test queue
- Confirm clicking tabs restores independent masks and transforms.
- Confirm custom added tabs scroll and remain selectable in narrow layouts.
- Confirm color-change button applies only to selected tab.
- Confirm selection survives switching tabs, editing, and pose changes.

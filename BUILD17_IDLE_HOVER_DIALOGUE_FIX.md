# Build 1.7 — Empty floating dialogue on idle cursor

## Report
After Build 1.6, a blank floating dialogue/bubble still appears when the cursor pauses in the combined editor. An earlier Build 1.3 change replaced the custom SHS tool cursor with a Qt crosshair, but that does not address Qt hover tooltips. The exact Windows popup was not reproduced in this Linux environment.

## Scoped correction
`main.py` adds a `CanvasHoverTipGuard`, installed only on the SHS artwork canvas and Slime Wizard artwork canvas. It suppresses native `ToolTip` events there and hides a leftover tooltip on canvas entry or editor-tab switch. The original Wizard canvas's informational tooltip is disabled in the host; its help is still available on the Transform controls. **Normal tooltips on other widgets remain available**, and the Slime Buddy portrait, guidance bubble, and enable/disable toggle are not removed.

The change is intentionally limited to UI hover behavior. The pixel artwork and all save, frame, Slimer, Chameleon, Eyedropper and SHS↔Wizard handoff logic remain unchanged.

## QA
Run `python -m pytest tests -q` and `python main.py --smoke-test` in the Windows GitHub Actions build. In the installed application, leave the mouse stationary for several seconds over a blank and a painted canvas position on each tab. No blank floating dialogue should appear; check the standard buttons still provide helpful tooltips. In Wizard, Buddy ON should still show tips and Buddy OFF should hide its tips.

If the box remains, capture a screenshot including the pointer and the surrounding UI to identify its source. This is a scoped fix for canvas hover tooltips, not a claim that an unseen Windows-native popup has been definitively diagnosed.

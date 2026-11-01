# Phase 14: overlapping source-layer preservation

When Move Original Pixels is enabled, selected rendered pixels must not erase every underlying visible source layer at the same canvas position. The erase pass now traverses visible layers from top to bottom and consumes the selection mask only where a layer contains an actual pixel. Covered lower layers remain intact.

Confirm All Placements still derives all tab transforms from the same unmodified render, with tab-order precedence where transformed outputs overlap.

Windows follow-up: stack two colored layers at the same position, select the upper visible pixel, Confirm All Placements with Move Original checked, and verify the lower layer remains intact; also test partially transparent layers and off-canvas layers.

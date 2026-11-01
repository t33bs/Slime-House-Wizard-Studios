# Phase 1 — Place as Layer / Place Frame collision report

User observed that placement appears to override other layers and that generated layers share the same name. User suspects Place Frame may be the offending action.

Implemented: explicit Place as Layer now always calls import_part with a new name, Slimer Layer 001, Slimer Layer 002, etc., avoiding existing names. Regression assertion added.

NOT YET VERIFIED/FIXED: visual layer-overwriting behavior in Windows; distinguish whether Place as Layer, Place Frame, or Move Original clearing source layers causes it. Do not mark the issue resolved until reproducing and validating all three cases. Place Frame currently reuses a canonical Slimer pose overlay intentionally, and its pose snapshot isolation needs GUI verification. Test both Move Original checked and unchecked; verify other layers and saved poses remain unchanged.

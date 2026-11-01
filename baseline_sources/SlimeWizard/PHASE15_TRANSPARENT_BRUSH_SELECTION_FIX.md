# Phase 52 — Transparent brush selection fix

Slimer now intersects the brush mask with visible artwork before Move Original preflight, layer creation, and pending source erasure. This prevents a selection brush stroke that crosses empty canvas from rejecting an otherwise valid move. Fully transparent selections still reject. Nonzero-alpha artwork remains selected, and fractional-alpha safety checks remain in place. No changes to Copy Pixels or Place Frame semantics.

Windows GUI workflow still requires testing; repository untouched.

# Phase 15 — staged destination safety

Apply Move now rejects a staged layer that is hidden, empty or entirely outside the canvas before destructive source erasure. This preserves original pixels on invalid destinations. Includes a regression test asserting validation precedes erase.

Automated suite: 387 passed, 9 skipped, 12 subtests passed. Windows GUI not verified. Consecutive Apply Move and save/reopen integration still require testing. No GitHub working tree was modified.

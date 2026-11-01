# Phase 15 — Require staged asset identity before Apply Move

Apply Move no longer accepts a numeric pending-layer row without the actual
staged asset object. An index may be stale or reused after Undo, deletion,
project reload, or another asset operation. The action now rejects the
unverified transaction without touching artwork. A verified staged object is
still located by identity in the current asset list.

This closes a wrong-asset confirmation path; it does not prove that consecutive
Move Original operations are fixed. Windows GUI verification is outstanding.

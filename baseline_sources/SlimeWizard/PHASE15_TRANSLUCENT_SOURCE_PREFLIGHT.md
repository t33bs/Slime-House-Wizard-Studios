# Phase 15 — Translucent source preflight

The untransformed fallback used by Move Original Pixels must not erase a selected semi-transparent pixel as if it were opaque. The preflight now rejects a selection whose contributing rendered pixels have fractional alpha (1–254), while continuing to accept fully opaque pixels. Copy Pixels is unaffected. Regression test exercises both cases through the actual method body.

Windows Qt GUI tests remain skipped in this environment. GitHub working tree was not modified.

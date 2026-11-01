# Phase 67 — Live editing-table signal gate

The existing three-consecutive-Move Original Pixels Qt regression used to call
`update_asset()` explicitly after changing the X spinbox. This could conceal a
broken Qt `valueChanged` connection. It now asserts the model changes from
`QSpinBox.setValue()` alone, then confirms each staged layer.

A second real Qt integration regression exercises two Copy Pixels rounds through
the same signal pathway, checking the independent assets, original pixel, and
unchanged animation-frame count.

These are regression tests, **not** a confirmed production fix. PySide6 is
unavailable in the headless test environment; run the tests on Windows with
PySide6 to validate the actual UI. GitHub working tree was not modified.

"""Opt-in isolation for PySide6 GUI tests that construct real Suite windows.

The production application schedules its crash-recovery prompt on the first
Qt event-loop cycle. With QT_QPA_PLATFORM=offscreen, that modal prompt is
invisible and hangs pytest when the user's real recovery snapshots exist.

This fixture is intentionally NOT autouse: recovery-specific tests retain the
real recovery API. GUI tests explicitly opt in via usefixtures.
"""
import pytest


@pytest.fixture
def isolate_gui_recovery(monkeypatch):
    import friendly_animator as app

    # Prevent the invisible modal prompt. Leave the production feature intact.
    monkeypatch.setattr(app.Suite, 'offer_recovery', lambda self: None)

    # The GUI's closeEvent() normally deletes a recovery for each open project.
    # A test window must never delete or overwrite a user's real recovery data.
    monkeypatch.setattr(app, 'discard_project_recovery', lambda *args, **kwargs: None)
    monkeypatch.setattr(app, 'write_project_recovery', lambda *args, **kwargs: None)

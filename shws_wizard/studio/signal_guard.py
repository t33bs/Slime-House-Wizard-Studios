"""Preserve Qt widget signal state during programmatic UI updates."""
from contextlib import contextmanager

@contextmanager
def blocked_signals(widget):
    previous = widget.blockSignals(True)
    try:
        yield
    finally:
        widget.blockSignals(previous)

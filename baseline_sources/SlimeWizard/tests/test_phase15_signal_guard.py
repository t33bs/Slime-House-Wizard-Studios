import pytest
from studio.signal_guard import blocked_signals

class FakeWidget:
    def __init__(self, blocked=False):
        self.blocked = blocked
        self.calls = []
    def blockSignals(self, value):
        previous = self.blocked
        self.blocked = value
        self.calls.append(value)
        return previous

@pytest.mark.parametrize("initial", [False, True])
def test_preserves_previous_state(initial):
    widget = FakeWidget(initial)
    with blocked_signals(widget):
        assert widget.blocked
    assert widget.blocked is initial

def test_restores_state_on_exception():
    widget = FakeWidget()
    with pytest.raises(ValueError):
        with blocked_signals(widget):
            raise ValueError('test')
    assert not widget.blocked

def test_nested_signal_blocks_remain_blocked():
    widget = FakeWidget()
    with blocked_signals(widget):
        with blocked_signals(widget):
            assert widget.blocked
        assert widget.blocked
    assert not widget.blocked

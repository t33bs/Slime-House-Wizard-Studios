"""Monotonic, pause-safe timing for the creature preview."""
import time


class PlaybackClock:
    def __init__(self, now=None):
        self._now = now or time.monotonic
        self._last = None

    def resume(self):
        self._last = self._now()

    def pause(self):
        self._last = None

    def delta_ms(self):
        if self._last is None:
            self.resume()
            return 0.0
        current = self._now()
        delta = max(0.0, (current - self._last) * 1000.0)
        self._last = current
        return delta

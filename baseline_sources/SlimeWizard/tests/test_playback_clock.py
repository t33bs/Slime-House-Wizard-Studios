import unittest
from studio.playback_clock import PlaybackClock


class PlaybackClockTests(unittest.TestCase):
    def test_real_elapsed_time_not_assumed_timer_interval(self):
        current = [10.0]
        clock = PlaybackClock(lambda: current[0])
        clock.resume()
        current[0] += .12
        self.assertAlmostEqual(clock.delta_ms(), 120)
        current[0] += .03
        self.assertAlmostEqual(clock.delta_ms(), 30)

    def test_paused_time_not_counted(self):
        current = [0.0]
        clock = PlaybackClock(lambda: current[0])
        clock.resume()
        current[0] = .1
        self.assertAlmostEqual(clock.delta_ms(), 100)
        clock.pause()
        current[0] = 100.0
        clock.resume()
        current[0] = 100.02
        self.assertAlmostEqual(clock.delta_ms(), 20)

    def test_clock_handles_uninitialized_and_backwards_time(self):
        current = [5.0]
        clock = PlaybackClock(lambda: current[0])
        self.assertEqual(clock.delta_ms(), 0)
        current[0] = 4.0
        self.assertEqual(clock.delta_ms(), 0)

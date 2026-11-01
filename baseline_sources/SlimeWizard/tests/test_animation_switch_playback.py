"""Source-level checks for animation switching without a Windows GUI."""
import unittest
from pathlib import Path

SOURCE = (Path(__file__).resolve().parents[1] / 'friendly_animator.py').read_text()

class AnimationSwitchPlaybackTests(unittest.TestCase):
    def test_switch_rebases_clock_and_refreshes_preview(self):
        method = SOURCE.split('    def change_anim(self,name):', 1)[1].split('    def select_step(self,index):', 1)[0]
        self.assertIn('self.restart_playback()', method)
        self.assertIn('self.refresh_preview()', method)

    def test_restart_pauses_clock_when_not_playing(self):
        method = SOURCE.split('    def restart_playback(self,*_):', 1)[1].split('    def tick(self):', 1)[0]
        self.assertIn('self.playback_clock.resume()', method)
        self.assertIn('self.playback_clock.pause()', method)

if __name__ == '__main__':
    unittest.main()

import unittest
from studio.slime_buddy import STATIONS,station_guide
class BuddyTests(unittest.TestCase):
 def test_all_stations_have_help(self):
  for station in STATIONS:
   text=station_guide(station)
   self.assertIn('How:',text)
   self.assertIn('Creative freedom:',text)
 def test_guidance_does_not_prescribe_creature_design(self):
  for station in STATIONS:
   self.assertNotIn('must have legs',station_guide(station).lower())
 def test_preview_guidance_is_only_for_actual_work(self):
  self.assertNotIn('Compare',STATIONS)
  guide=station_guide('Preview').lower()
  self.assertIn('playback',guide)
  self.assertNotIn('reference',guide)
  self.assertNotIn('upload',guide)
 def test_unknown_station(self):
  with self.assertRaises(KeyError): station_guide('No station')
if __name__=='__main__':unittest.main()

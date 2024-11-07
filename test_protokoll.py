import datetime
import unittest
from kivy.clock import Clock
from protokoll import ProtokollApp

class TestProtokollApp(unittest.TestCase):
    def setUp(self):
        # Initialisiere die App
        self.app = ProtokollApp()
        self.app.build()

    def test_set_default_values(self):
        # Plane den Aufruf von set_default_values in der nächsten Frame
        Clock.schedule_once(lambda dt: self.app.set_default_values(), 0)
    
        # Starte den Kivy-Eventloop für einen Frame
        Clock.tick()
    
        # Überprüfe die Standardwerte
        now = datetime.now()
        current_date = now.strftime("%Y-%m-%d")
        current_time = now.strftime("%H:%M")
    
        self.assertEqual(self.app.root.ids.datum.text, current_date)
        self.assertEqual(self.app.root.ids.beginn.text, current_time)
        self.assertEqual(self.app.root.ids.ende.text, current_time)

    
if __name__ == '__main__':
    unittest.main()
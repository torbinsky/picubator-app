from picubator import Heater

import unittest
from mock import Mock

class TestHeater(unittest.TestCase):
 
    def setUp(self):
        pass
 
    def test_heater_knows_its_on(self):
        heater = Heater(22, Mock())
        # Ensure default off
        self.assertFalse(heater.isOn(), 'Heater should be off by default')
        # Ensure turning it on works
        heater.on()
        self.assertTrue(heater.isOn(), 'Heater should be on after on()')
        # Ensure turning it off works
        heater.off()
        self.assertFalse(heater.isOn(), 'Heater should be off after off()')
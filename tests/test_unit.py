import unittest
from mock import patch
import logging

class TestOps(unittest.TestCase):
 
    def setUp(self):
        pass
 
    @patch("picubator.Dash")
    @patch("picubator.Camera")
    @patch("picubator.Heater")
    @patch("picubator.Sensor")
    @patch("picubator.Brain")
    def test_listens_to_brain(self, Brain, Sensor, Heater, Camera, Dash):
        from picubator import Unit
        unit = Unit(Brain(),Camera(),Sensor(),Heater(),Dash())
        unit.sensor.read.return_value = (42, 24)
        unit.on()
        unit.brain.should_heat.return_value = True
        unit.run_cycle()
        unit.heater.on.assert_called_once_with()
        
        unit.brain.should_heat.return_value = False
        unit.run_cycle()
        unit.heater.off.assert_called_once_with()
    
    @patch("picubator.Dash")
    @patch("picubator.Camera")
    @patch("picubator.Heater")
    @patch("picubator.Sensor")
    @patch("picubator.Brain")
    def test_listens_to_toggle(self, Brain, Sensor, Heater, Camera, Dash):
        from picubator import Unit
        unit = Unit(Brain(),Camera(),Sensor(),Heater(),Dash())
        unit.sensor.read.return_value = (42, 24)
        unit.brain.should_heat.return_value = True
        unit.brain.should_image.return_value = False
        
        # Validate initial state
        self.assertEqual(unit.state, 'OFFLINE')
        # Toggle the picubator on
        unit.dash.read_toggle.return_value = True
        unit.run_cycle()
        self.assertEqual(unit.state, 'ONLINE')
        unit.heater.on.assert_called_once_with()
        unit.brain.should_image.return_value = True
        unit.run_cycle()
        unit.camera.capture_base64.assert_called_once_with()
        self.assertEqual(unit.state, 'ONLINE')
        
        # Toggle the picubator off, Brain still says should heat
        unit.dash.read_toggle.return_value = False
        unit.run_cycle()
        self.assertEqual(unit.state, 'OFFLINE')
        unit.brain.reset.assert_called_once_with() # Brain should get reset on an off
        unit.heater.off.assert_called_once_with() # toggle should result in heat off
    
    @patch("picubator.Dash")
    @patch("picubator.Camera")
    @patch("picubator.Heater")
    @patch("picubator.Sensor")
    @patch("picubator.Brain")
    def test_exception_handling(self, Brain, Sensor, Heater, Camera, Dash):
        from picubator import Unit
        unit = Unit(Brain(),Camera(),Sensor(),Heater(),Dash())
        unit.sensor.read.return_value = (42, 24)
        
        # Ensure that we get an exception from the dash
        unit.dash.send_status.side_effect = Exception('dash send_status not available!')
        unit.dash.read_toggle.side_effect = Exception('dash read_toggle not available!')
        with self.assertRaises(Exception):
            unit.dash.read_toggle()
        
        # Ensure that our run_cycle has no issue with exceptions
        unit.run_cycle()
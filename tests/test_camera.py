from picubator.camera import Camera

import unittest
from mock import Mock

class TestCamera(unittest.TestCase):
 
    def setUp(self):
        pass
 
    def test_uses_light(self):
        light = Mock()
        cameraAPI = Mock()
        camera = Camera(200,200,light, cameraAPI)
        # validate light not turned off if it was on
        light.isOn.return_value = True
        camera.capture_base64()
        light.on.assert_called_once()
        self.assertEqual(light.off.call_count, 0)
        
        # validate light is turned off if it was off
        light.isOn.return_value = False
        camera.capture_base64()
        light.on.assert_called_with()
        self.assertEqual(light.off.call_count, 1)
from picubator.ops import Brain

from random import randint

import unittest

class TestOps(unittest.TestCase):
 
    def setUp(self):
        pass
 
    def test_initial_state(self):
        brain = Brain()
        # validate initial state
        self.assertEqual(brain.current_temp, -9999)
        self.assertEqual(brain.state, 'standby')
        self.assertEqual(brain.overshoot_temp, -9999)
        self.assertEqual(brain.target_temp, -9999)
        self.assertEqual(brain.should_heat(), False)
    
    def test_basic_heat_up_cooldown(self):
        brain = Brain()
        # ensure we set our internal target value
        brain.set_target(20)
        self.assertEqual(brain.target_temp, 20)
        # should still be in standby
        self.assertEqual(brain.should_heat(), False)
        brain.report_temp(10)
        self.assertEqual(brain.current_temp, 10)
        self.assertEqual(brain.state, 'heating')
        self.assertEqual(brain.should_heat(), True)
        
        # Simulate a slow heatup, and ensure we constantly want to heat up until
        # we hit an overshoot which should be 0.5 > target
        for x in range(11, 20):
            brain.report_temp(x)
            self.assertEqual(brain.should_heat(), True)
            
        # Now exceed the overshoot and validate no more heating
        brain.report_temp(21)
        for x in range(11, 20):
            brain.report_temp(x)
            self.assertEqual(brain.should_heat(), True)
        
        # test a few other values and ensure heat/cool toggling
        brain.report_temp(23)
        self.assertEqual(brain.should_heat(), False)
        brain.report_temp(18)
        self.assertEqual(brain.should_heat(), True)
        brain.report_temp(17)
        self.assertEqual(brain.should_heat(), True)
        brain.report_temp(18)
        self.assertEqual(brain.should_heat(), True)
        brain.report_temp(20)
        self.assertEqual(brain.should_heat(), True)
        brain.report_temp(21)
        self.assertEqual(brain.should_heat(), False)
        
    def test_error_mode(self):
        brain = Brain()
        brain.set_target(37)
        brain.report_temp(15)
        self.assertEqual(brain.should_heat(), True)
        self.assertEqual(brain.state, 'heating')
        # Trigger an error by jumping temperature too much
        brain.report_temp(25.01)
        self.assertEqual(brain.state, 'error')
        self.assertEqual(brain.should_heat(), False)
        # Reprot something still way out
        brain.report_temp(26)
        self.assertEqual(brain.state, 'error')
        self.assertEqual(brain.should_heat(), False)
        # Now report something way too low
        brain.report_temp(2)
        self.assertEqual(brain.state, 'error')
        self.assertEqual(brain.should_heat(), False)
        # Now report something reasonable (based on what the last good value was)
        brain.report_temp(20)
        self.assertEqual(brain.state, 'heating') # should back in heating
        self.assertEqual(brain.should_heat(), True)
    
    def test_changing_target_up_down(self):
        brain = Brain()
        brain.set_target(37)
        brain.report_temp(15)
        self.assertEqual(brain.should_heat(), True)
        brain.set_target(16)
        self.assertEqual(brain.should_heat(), True)
        brain.set_target(15.6)
        self.assertEqual(brain.should_heat(), True)
        brain.set_target(15.4)
        self.assertEqual(brain.should_heat(), False)
        brain.set_target(16)
        self.assertEqual(brain.should_heat(), True)
        brain.set_target(14)
        self.assertEqual(brain.should_heat(), False)
        brain.set_target(14)
        self.assertEqual(brain.should_heat(), False)
        brain.set_target(13)
        self.assertEqual(brain.should_heat(), False)
        brain.set_target(37)
        self.assertEqual(brain.should_heat(), True)
        
if __name__ == '__main__':
    unittest.main()
from picubator.ops import Brain

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
    
    def test_basic_heat_up(self):
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
        # Now exceed the overshoot
        brain.report_temp(21)
        self.assertEqual(brain.should_heat(), False)
 
if __name__ == '__main__':
    unittest.main()
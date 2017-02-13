import logging
import time
from transitions import Machine

# Initialize logging
logger = logging.getLogger(__name__)

class Brain(Machine):
    'The ops center for picubator'
    
    states = ['standby','heating','cooling','error']

    def __init__(self):
        Machine.__init__(self, states=Brain.states, initial='standby')
        # Trigger 'report_error' always goes to error state
        self.add_transition('report_error','*','error')
        self.add_transition('heat_up', ['standby','cooling', 'heating'], 'heating', 
        before='before_heat_up')
        self.add_transition('cool_down', ['standby','heating', 'cooling'], 'cooling',
        before='before_cool_down')
        # Only a valid report trigger can get us to transition out of error
        self.add_transition('report_valid', 'error', 'standby')
        # All other triggers keep us in error
        self.add_transition('*','error','error')
        # Valid reports are allowed in other states, but don't do any transition
        self.add_transition('report_valid', 'heating', 'heating')
        self.add_transition('report_valid', 'cooling', 'cooling')
        self.add_transition('report_valid', 'standby', 'standby')
        self.reset()

    def reset(self):
        self.set_state('standby')
        self.target_temp = -9999
        self.current_temp = -9999
        self.overshoot_temp = -9999
        self.time_to_next_image = 0
        self.min_seconds_between_images = 60

    def should_image(self):
        current_time = time.time()
        if(current_time > self.time_to_next_image):
            logger.debug("Yes, we should image")
            self.time_to_next_image = current_time + self.min_seconds_between_images
            return True
        else:
            logger.debug("No, we shouldn't image until %s", self.time_to_next_image)
            return False

    def should_heat(self):
        # We should heat only if we are in the heating state
        return self.is_heating()
        
    def set_target(self, target):
        # noop for same temp
        if(self.target_temp == target):
            return
        
        self.target_temp = target
        # Default to cooling down, but we will evaluate after to check what we
        # should really do
        self.cool_down()
        self.evaluate(self.current_temp)

    def report_temp(self, temp):
        logger.info("Received a report of temperature: %s", temp)
        
        # If we get a negative temperature report, sensor is misbehaving
        ## Note: this is based on my setup and may not be a good check for other
        ## environments
        if(temp < 0):
            self.report_error()
            return
        
        # If we have a previous report, a drastic swing in temp is probably a sensor error
        ## -9999 is our uninitialized temperature
        if(self.current_temp > -9999):
            # If we get a massive temperature swing, consider it an error
            if(temp > self.current_temp + 10 or temp < self.current_temp - 10):
                self.report_error()
                return
        
        # Check if we are in the initial state
        if(self.current_temp == -9999):
            # This is our first temperature report, so just use it
            self.current_temp = temp
            
        # At this point, we consider the temperature report to be valid
        self.report_valid()
        
        # decide if we should heat or cool now
        self.evaluate(temp)
        
        # Update our last known temperature
        self.current_temp = temp
    
    def evaluate(self, next_temp):
        # If we haven't had a target or valid current temperature, we are done
        if(next_temp == -9999 or self.target_temp == -9999):
            return
        
        # We have a valid target and current temp, decide if we should heat or cool
        if self.is_standby():
            # If we are in standby, decide if we should go to heating or cooling
            if(next_temp < self.target_temp):
                self.heat_up()
            else:
                self.cool_down()
        elif self.is_heating():
            # If we are heating and we are above the overshoot, start cooling
            if next_temp > self.overshoot_temp:
                self.cool_down()
        elif self.is_cooling():
            # If we are cooling and we are below the overshoot, start heating
            if next_temp < self.overshoot_temp:
                self.heat_up()
    
    def before_cool_down(self):
        logger.info("I am cooling down. I'll allow a 0.5 target undershoot.")
        self.overshoot_temp = self.target_temp - 0.5
        
    def before_heat_up(self):
        logger.info("I am heating up. I'll allow a 0.5 target overshoot.")
        self.overshoot_temp = self.target_temp + 0.5

import logging


# Initialize logging
logger = logging.getLogger(__name__)

class Brain:
    'The ops center for picubator'

    def __init__(self):
        self.reset()

    def reset(self):
        self.target_temp = 0
        self.current_temp = -1
        self.heating_up = True
        self.error_count = 0

    def should_heat(self):
        # Don't heat if our error count gets too high
        if self.error_count > 10:
            logger.warn("Error count[%s] exceeds 10, heat is off for safe mode", self.error_count)
            return False

        # If we're heating up, then allow some above threshold overshoot
        if self.heating_up and ((self.target_temp + 0.5) > self.current_temp):
            logger.info("Heating up with 0.5 overshoot. target[%s], current_temp[%s]", self.target_temp, self.current_temp)
            return True
        # Alternatively, if we're cooling down, allow some below threshold
        elif (not self.heating_up) and ((self.target_temp - 0.5) > self.current_temp):
            logger.info("Cooling down with 0.5 undershoot. target[%s], current_temp[%s]", self.target_temp, self.current_temp)
            return False
        else:
            logger.info("It's getting too hot! Cooling down.")
            return False

    def report_temp(self, temp):
        logger.info("Received a report of temperature: %s", temp)

        # Check if we've gotten our first report yet
        if(self.current_temp > 0):
            # Check if the temperature makes sense (it shouldn't ever swing wildly)
            if(temp > self.current_temp + 10 or temp < self.current_temp - 10):
                logger.warn("Received suspicious temperature [%s], ignoring report")
                self.error_count += 1
                return
            else:
                # reset error count
                logger.debug("Temp is reasonable, resetting error count")
                self.error_count = 0

        if(temp > self.current_temp):
            # heating up
            logger.info("Report indicates I am heating up.")
            self.heating_up = True
        else:
            # cooling down
            logger.info("Report indicates I am cooling down.")
            self.heating_up = False

        # Update our last known temperature
        self.current_temp = temp

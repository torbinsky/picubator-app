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
        self.goal_temp = 0

    def should_heat(self):
        # Don't heat if our error count gets too high
        if self.error_count > 10:
            logger.warn("Error count[%s] exceeds 10, heat is off for safe mode", self.error_count)
            return False

        return self.current_temp < self.goal_temp

    def report_temp(self, temp):
        logger.info("Received a report of temperature: %s", temp)

        # Check if we've gotten our first report yet
        if(self.current_temp > 0):
            # Check if the temperature makes sense (it shouldn't ever swing wildly)
            if(temp > self.current_temp + 10 or temp < self.current_temp - 10):
                logger.warn("Received suspicious temperature [%s], ignoring report")
                self.error_count += 1
                return
            elif self.error_count > 0:
                # reset error count
                logger.info("Temp is reasonable, resetting error count")
                self.error_count = 0

        if temp > self.current_temp:
            # heating up
            logger.info("Report indicates I am heating up. I'll allow a 0.5 target overshoot.")
            self.heating_up = True
            self.goal_temp = self.target_temp + 0.5
        elif temp < self.current_temp:
            # cooling down
            logger.info("Report indicates I am cooling down. I'll allow a 0.5 target undershoot.")
            self.heating_up = False
            self.goal_temp = self.target_temp - 0.5

        # Update our last known temperature
        self.current_temp = temp

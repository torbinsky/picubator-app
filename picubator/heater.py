import logging

import RPi.GPIO as io

# Initialize logging
logger = logging.getLogger(__name__)

class Heater:
    'Represents a heater (or anything power controllable really) that can be turned on/off'

    def __init__(self, pp):
        self.power_pin = pp

        # Initialize power control port for our heating unit
        logger.info('Initializing power...')
        io.setmode(io.BCM)
        io.setup(self.power_pin, io.OUT)
        self.off()
        logger.info('Power initialized')

    def on(self):
        logger.debug('HEAT ON')
        io.output(self.power_pin, io.HIGH)
        self.heating = True

    def off(self):
        logger.debug('HEAT OFF')
        io.output(self.power_pin, io.LOW)
        self.heating = False
    
    def isOn(self):
        return self.heating

    def __del__(self):
        logger.debug("Cleaning up GPIO state")
        io.cleanup()

import logging

try:
    import RPi.GPIO as io
except ImportError:
    print(
    '-------------------------------------------------------------------------')
    print(
    ' WARNING: Unable to import RPi.GPIO library.')
    print(
    '-------------------------------------------------------------------------')

# Initialize logging
logger = logging.getLogger(__name__)

class Heater:
    'Represents a heater (or anything power controllable really) that can be turned on/off'

    def __init__(self, pp, ioAPI=None):
        self.power_pin = pp
        self.io = ioAPI or io
        # Initialize power control port for our heating unit
        logger.info('Initializing power...')
        self.io.setmode(self.io.BCM)
        self.io.setup(self.power_pin, self.io.OUT)
        self.off()
        logger.info('Power initialized')

    def on(self):
        logger.debug('HEAT ON')
        self.io.output(self.power_pin, self.io.HIGH)
        self.heating = True

    def off(self):
        logger.debug('HEAT OFF')
        self.io.output(self.power_pin, self.io.LOW)
        self.heating = False
    
    def isOn(self):
        return self.heating

    def __del__(self):
        logger.debug("Cleaning up GPIO state")
        self.io.cleanup()

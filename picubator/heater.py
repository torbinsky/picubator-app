import RPi.GPIO as io

# Initialize logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

power_pin = None

def init(pp):
    power_pin = pp

    # Initialize power control port for our heating unit
    logger.info('Initializing power...')
    io.setmode(io.BCM)
    io.setup(power_pin, io.OUT)
    io.output(power_pin, False) # default turn off
    logger.info('Power initialized')

def on():
    logger.debug('HEAT ON')
    io.output(power_pin, True)

def off():
    logger.debug('HEAT OFF')
    io.output(power_pin, False)

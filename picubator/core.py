import time
from datetime import datetime
import json

import heater
import sensor

# Initialize logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load application config file
logger.info('Loading configuration...')
with open('config.json', 'r') as f:
    config = json.load(f)

# Initialize state from config settings
logger.debug('Initializing state...')
sensor.init(config['sensor.type'], config['sensor.pinNum'])
heater.init(config['heat.powerControlPinNum'])
logger.info('Initialization complete')

def do_main_program():
    logger.debug('Running...')
    while True:
        logger.debug('Reading temp,humidity...')
        humidity, temp = sensor.read()
        logger.debug('Temp[%s] Humidity[%s]', temp, humidity)

        # Turn the heat off if we hit threshold temp, on otherwise
        if(temp > threshold):
            heater.off()
        else:
            heater.on()

        #record_reading(humidity, temp)

        time.sleep(10)

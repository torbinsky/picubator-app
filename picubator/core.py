import time
from datetime import datetime
import json
import logging
import logging.config
import os

# Load logging config before our modules so we configure those modules' logging as well
log_config_path = os.path.join(os.path.dirname(__file__), '../logging_config.ini')
logging.config.fileConfig(log_config_path)

from heater import Heater
from sensor import Sensor
from iotdash import Dash

logger = logging.getLogger(__name__)

def init():
    global sensor, heater, dash
    # Load application config file
    logger.info('Loading configuration...')
    config_path = os.environ.get('PICUBATOR_CONFIG', 'config.json')
    with open(config_path, 'r') as f:
        config = json.load(f)

    # Initialize state from config settings
    logger.debug('Initializing state...')
    sensor = Sensor(config['sensor']['type'], config['sensor']['pinNum'])
    heater = Heater(config['heat']['powerControlPinNum'])
    dash = Dash(key=config['adafruitio']['key'], temp_feed=config['adafruitio']['temperatureFeedName'], humidity_feed=config['adafruitio']['humidityFeedName'], toggle_feed=config['adafruitio']['mainToggleFeedName'], threshold_feed=config['adafruitio']['temperatureThresholdFeedName'])
    logger.info('Initialization complete')

    logger.debug('Running...')

def main():
    while True:
        if(dash.read_toggle()):
            run_on()
        else:
            run_off()

def run_off():
    logger.debug('Picubator is toggled off')
    heater.off() # Make sure the heater is off!
    time.sleep(2)

def run_on():
    logger.debug('Reading temp,humidity...')
    humidity, temp = sensor.read()
    logger.debug('Temp[%s] Humidity[%s]', temp, humidity)

    threshold = dash.read_threshold()
    logger.debug('Temperature threshold is %s', threshold)

    # Turn the heat off if we hit threshold temp, on otherwise
    if(temp > threshold):
        heater.off()
    else:
        heater.on()

    dash.record(temp, humidity)

    time.sleep(10)

if __name__ == '__main__':
    main()

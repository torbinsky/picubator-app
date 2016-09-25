import time
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
from ops import Brain

logger = logging.getLogger(__name__)

def init():
    global sensor, heater, dash, brain

    # Load application config file
    logger.info('Loading configuration...')
    config_path = os.environ.get('PICUBATOR_CONFIG', 'config.json')
    with open(config_path, 'r') as f:
        config = json.load(f)

    brain = Brain()

    # Initialize state from config settings
    logger.debug('Initializing state...')
    sensor = Sensor(config['sensor']['type'], config['sensor']['pinNum'])
    heater = Heater(config['heat']['powerControlPinNum'])
    dash = Dash(key=config['adafruitio']['key'], temp_feed=config['adafruitio']['temperatureFeedName'], humidity_feed=config['adafruitio']['humidityFeedName'], toggle_feed=config['adafruitio']['mainToggleFeedName'], threshold_feed=config['adafruitio']['temperatureThresholdFeedName'],status_feed=config['adafruitio']['statusFeedName'])
    dash.send_status("Picubator connected.")
    logger.info('Initialization complete')

    logger.debug('Running...')

def main():
    toggle_on = False
    online = False
    while True:
        try:
            toggle_on = dash.read_toggle()
        except Exception:
            logger.warn("Encountered exception communicating with dash")
            pass

        if(toggle_on):
            run_on()
            if(not online):
                dash.send_status("Picubator mode is now ONLINE.")
            online = True
        else:
            run_off()
            if(online):
                dash.send_status("Picubator mode is now STAND_BY.")
            online = False

def run_off():
    logger.debug('Picubator is toggled off')
    heater.off() # Make sure the heater is off!
    brain.reset()
    time.sleep(5)

def run_on():
    logger.debug('Reading temp,humidity...')
    humidity, temp = sensor.read()
    logger.debug('Temp[%s] Humidity[%s]', temp, humidity)
    brain.report_temp(temp)

    try:
        brain.target_temp = dash.read_threshold()
        logger.debug('Temperature threshold is %s', brain.target_temp)
    except Exception:
        pass

    # Turn the heat off if we hit threshold temp, on otherwise
    if(brain.should_heat()):
        heater.on()
    else:
        heater.off()

    # Attempt to update our iot dashboard
    try:
        dash.record(temp, humidity)
    except Exception:
        pass

    time.sleep(5)

if __name__ == '__main__':
    main()

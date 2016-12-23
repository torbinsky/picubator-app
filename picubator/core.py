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
from camera import Camera

logger = logging.getLogger(__name__)

def init():
    global sensor, heater, dash, brain, camera

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
    camera = Camera(config['camera']['xRes'], config['camera']['yRes'])
    dash = Dash(key=config['adafruitio']['key'], temp_feed=config['adafruitio']['temperatureFeedName'], humidity_feed=config['adafruitio']['humidityFeedName'], toggle_feed=config['adafruitio']['mainToggleFeedName'], threshold_feed=config['adafruitio']['temperatureThresholdFeedName'],status_feed=config['adafruitio']['statusFeedName'], heater_status_feed=config['adafruitio']['heaterStatusFeedName'], camera_feed=config['adafruitio']['cameraFeedName'])
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
            if(not online):
                try:
                    dash.send_status("Picubator mode is now ONLINE.")
                except Exception:
                    pass
            run_on()
            online = True
        else:
            if(online):
                try:
                    dash.send_status("Picubator mode is now STAND_BY.")
                except Exception:
                    pass
            run_off()
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

    # Turn the heat off if we hit threshold temp, on otherwise
    if(brain.should_heat()):
        heater.on()
    else:
        heater.off()

    # Attempt to update our iot dashboard
    try:
        brain.target_temp = dash.read_threshold()
        dash.heater_status(heater.heating)
        logger.debug('Temperature threshold is %s', brain.target_temp)
        dash.record(temp, humidity)
        logger.debug('Sending camera capture to dash...')
        dash.send_image(camera.capture_base64())
        logger.debug("Finished main run loop.")
    except Exception:
        pass

    time.sleep(5)

if __name__ == '__main__':
    main()

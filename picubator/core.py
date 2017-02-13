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
from transitions import Machine

logger = logging.getLogger(__name__)

class Unit(Machine):
    
    def turned_on(self):
        logger.info('Picubator turned ON')
        self.dash.send_status("Picubator is ON")
    
    def turned_off(self):
        logger.info('Picubator turned OFF')
        self.dash.send_status("Picubator is OFF")
    
    def __init__(self):
        Machine.__init__(self, ['ONLINE','OFFLINE'], initial='OFFLINE')
        # New transitions
        self.add_transition('on', ['OFFLINE'], 'ONLINE', after='turned_on')
        self.add_transition('off',  ['ONLINE'], 'OFFLINE', after='turned_off')
        # Allowed to transition to same state
        self.add_transition('on', ['ONLINE'], 'ONLINE')
        self.add_transition('off',  ['OFFLINE'], 'OFFLINE')
    
        # Load application config file
        logger.info('Loading configuration...')
        config_path = os.environ.get('PICUBATOR_CONFIG', 'config.json')
        with open(config_path, 'r') as f:
            config = json.load(f)
    
        self.brain = Brain()
    
        # Initialize state from config settings
        logger.debug('Initializing state...')
        self.sensor = Sensor(config['sensor']['type'], config['sensor']['pinNum'])
        self.heater = Heater(config['heat']['powerControlPinNum'])
        self.camera = Camera(config['camera']['xRes'], config['camera']['yRes'], self.heater)
        self.dash = Dash(key=config['adafruitio']['key'], temp_feed=config['adafruitio']['temperatureFeedName'], humidity_feed=config['adafruitio']['humidityFeedName'], toggle_feed=config['adafruitio']['mainToggleFeedName'], threshold_feed=config['adafruitio']['temperatureThresholdFeedName'],status_feed=config['adafruitio']['statusFeedName'], heater_status_feed=config['adafruitio']['heaterStatusFeedName'], camera_feed=config['adafruitio']['cameraFeedName'])
        self.dash.send_status("Picubator connected.")
        logger.info('Initialization complete')
        logger.debug('Running...')
    
    def run_cycle(self):
        if self.state == 'ONLINE':
            logger.debug('Picubator running an online cycle')
            self.run_on()
        elif self.state == 'OFFLINE':
            logger.debug('Picubator running an offline cycle')
            self.run_off()
    
    def run_off(self):
        self.heater.off() # Make sure the heater is off!
        self.brain.reset()
        time.sleep(5)
    
    def run_on(self):
        logger.debug('Reading temp,humidity...')
        humidity, temp = self.sensor.read()
        logger.debug('Temp[%s] Humidity[%s]', temp, humidity)
        self.brain.report_temp(temp)
    
        # Turn the heat off if we hit threshold temp, on otherwise
        if self.brain.should_heat():
            self.heater.on()
        else:
            self.heater.off()
    
        # Attempt to update our iot dashboard
        try:
            self.brain.set_target(self.dash.read_threshold())
            self.dash.heater_status(self.heater.heating)
            logger.debug('Temperature threshold is %s', self.brain.target_temp)
            self.dash.record(temp, humidity)
            logger.debug('Sending camera capture to dash...')
            if(self.brain.should_image()):
                self.dash.send_image(self.camera.capture_base64())
            logger.debug("Finished main run loop.")
        except Exception:
            pass
        
        time.sleep(5)

def main():
    unit = Unit()
    while True:
        try:
            if dash.read_toggle():
                unit.on()
            else:
                unit.off()
        except:
            logger.error("Encountered an error, turning off!")
            unit.off()
        unit.run_cycle()
    
if __name__ == '__main__':
    main()

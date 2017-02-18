import time
import json
import logging
import logging.config
import os
from transitions import Machine

# Load logging config before our modules so we configure those modules' logging as well
log_config_path = os.path.join(os.path.dirname(__file__), '../logging_config.ini')
logging.config.fileConfig(log_config_path)

from heater import Heater
from sensor import Sensor
from camera import Camera
from ops import Brain
from iotdash import Dash

logger = logging.getLogger(__name__)

class Unit(Machine):
    'The main unit of the picubator'
    
    states = ['ONLINE','OFFLINE']
    
    def turned_on(self):
        logger.info('Picubator turned ON')
        self.dash.send_status("Picubator is ON")
    
    def turned_off(self):
        logger.info('Picubator turned OFF')
        self.brain.reset()
        # Attempt to update dash status, but ignore errors
        try:
            self.dash.send_status("Picubator is OFF")
        except:
            pass
    
    def __init__(self,brain,camera,sensor,heater,dash):
        Machine.__init__(self, states=Unit.states, initial='OFFLINE')
        # New transitions
        self.add_transition('on', ['OFFLINE'], 'ONLINE', after='turned_on')
        self.add_transition('off',  ['ONLINE'], 'OFFLINE', after='turned_off')
        # Allowed to transition to same state
        self.add_transition('on', ['ONLINE'], 'ONLINE')
        self.add_transition('off',  ['OFFLINE'], 'OFFLINE')
        
        self.brain = brain
        self.camera = camera
        self.sensor = sensor
        self.heater = heater
        self.dash = dash
    
    def run_cycle(self):
        # Safely try to update on/off from the dash toggle
        try:
            # update unit on/off from dash toggle
            if self.dash.read_toggle():
                self.on()
            else:
                self.off()
        except:
            # If we hit an error, log and turn the unit off
            logger.exception("Error during dash toggle read, turning off!")
            self.off()
        
        # Safely try to do the next run operations
        try:
            if self.is_ONLINE():
                logger.debug('Picubator running an online cycle')
                self.run_on()
            else:
                logger.debug('Picubator running an offline cycle')
                self.run_off()
        except:
            # If we hit an error, log and turn the unit off
            logger.exception("Error during run on/off")
    
    def run_off(self):
        self.heater.off() # Make sure the heater is off!

    def run_on(self):
        logger.debug('Starting ON run cycle...')
        humidity, temp = self.sensor.read()
        logger.debug('Temp[%s] Humidity[%s]', temp, humidity)
        self.brain.report_temp(temp)
        
        # Turn the heat off if we hit threshold temp, on otherwise
        if self.brain.should_heat():
            self.heater.on()
        else:
            self.heater.off()
        
        # Attempt to update our iot dashboard
        # Update target temp from dash
        self.brain.set_target(self.dash.read_threshold())
        logger.debug('Temperature threshold is %s', self.brain.target_temp)
        
        # Update dashboard heater status
        self.dash.heater_status(self.heater.heating)
        self.dash.record(temp, humidity)
        
        # Do image capture
        if(self.brain.should_image()):
            logger.debug('Sending camera capture to dash...')
            self.dash.send_image(self.camera.capture_base64())

def init():
    # Load application config file
    logger.info('Loading configuration...')
    config_path = os.environ.get('PICUBATOR_CONFIG', 'config.json')
    with open(config_path, 'r') as f:
        config = json.load(f)
    
    # Initialize state from config settings
    logger.debug('Initializing state...')
    brain = Brain()
    sensor = Sensor(config['sensor']['type'], config['sensor']['pinNum'])
    heater = Heater(config['heat']['powerControlPinNum'])
    camera = Camera(config['camera']['xRes'], config['camera']['yRes'], heater)
    dash = Dash(key=config['adafruitio']['key'], temp_feed=config['adafruitio']['temperatureFeedName'], humidity_feed=config['adafruitio']['humidityFeedName'], toggle_feed=config['adafruitio']['mainToggleFeedName'], threshold_feed=config['adafruitio']['temperatureThresholdFeedName'],status_feed=config['adafruitio']['statusFeedName'], heater_status_feed=config['adafruitio']['heaterStatusFeedName'], camera_feed=config['adafruitio']['cameraFeedName'])
    dash.send_status("Picubator connected.")
    unit = Unit(brain,camera,sensor,heater,dash)
    logger.info('Initialization complete')
    return unit
    
def main(unit=None):
    # Initialize unit if needed
    if unit is None:
        unit = init()
    
    # main loop
    while True:
        # run the main unit cycle
        unit.run_cycle()
        # slow the roll
        time.sleep(5)
    
if __name__ == '__main__':
    main()

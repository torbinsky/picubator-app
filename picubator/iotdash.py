import logging

from Adafruit_IO import Client

logger = logging.getLogger(__name__)

class Dash:
    'Represents an Adafruit IO Dashboard which gives input/output capabilities'

    def __init__(self, key):
        logger.debug("Initializing Adafruit IO client...")
        self.client = Client(key)
        logger.debug("Adafruit IO client initialized")

    def record(self, temp, humidity):
        logger.debug("temp[%s] rh[%s]", temp, humidity)
        self.client.send('picubator-temperature', temp)
        self.client.send('picubator-humidity', humidity)

    def read_toggle(self):
        toggle_state = self.client.receive('picubator-toggle').value
        logger.debug("Toggle state is %s", toggle_state)
        return toggle_state == "ON"

    def read_threshold(self):
        threshold = self.client.receive('picubator-threshold').value
        logger.debug("Threshold is %s", threshold)
        return int(threshold)

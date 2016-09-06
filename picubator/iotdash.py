import logging

from Adafruit_IO import Client

logger = logging.getLogger(__name__)

class Dash:
    'Represents an Adafruit IO Dashboard which gives input/output capabilities'

    def __init__(self, key, temp_feed='picubator-temperature', humidity_feed='picubator-humidity',
                toggle_feed='picubator-toggle', threshold_feed='picubator-threshold'
                ):
        logger.debug("Initializing Adafruit IO client...")
        self.client = Client(key)
        self.temp_feed = temp_feed
        self.humidity_feed = humidity_feed
        self.toggle_feed = toggle_feed
        self.threshold_feed = threshold_feed
        logger.debug("Adafruit IO client initialized")

    def record(self, temp, humidity):
        logger.debug("temp[%s] rh[%s]", temp, humidity)
        self.client.send(self.temp_feed, temp)
        self.client.send(self.humidity_feed, humidity)

    def read_toggle(self):
        toggle_state = self.client.receive(self.toggle_feed).value
        logger.debug("Toggle state is %s", toggle_state)
        return toggle_state == "ON"

    def read_threshold(self):
        threshold = self.client.receive(self.threshold_feed).value
        logger.debug("Threshold is %s", threshold)
        return int(threshold)

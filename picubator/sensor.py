import logging

try:
    import Adafruit_DHT
    sensor_types = {
        '11': Adafruit_DHT.DHT11,
        '22': Adafruit_DHT.DHT22,
        '2302': Adafruit_DHT.AM2302
    }
except ImportError:
    print(
    '-------------------------------------------------------------------------')
    print(
    ' WARNING: Unable to import Adafruit_DHT library.')
    print(
    '-------------------------------------------------------------------------')

# Initialize logging
logger = logging.getLogger(__name__)


class Sensor:
    'Represents a DHT type sensor that can provide temperature/humidity readings'

    def __init__(self, sensor_type, sensor_pin):
        self.sensor_type = sensor_types[sensor_type]
        self.sensor_pin = sensor_pin

    def read(self):
        humidity, temp = Adafruit_DHT.read_retry(self.sensor_type, self.sensor_pin)
        return (round(humidity, 2), round(temp, 2))

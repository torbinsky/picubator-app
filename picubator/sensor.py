import Adafruit_DHT

# Initialize logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

sensor_types = { '11': Adafruit_DHT.DHT11,
                '22': Adafruit_DHT.DHT22,
                '2302': Adafruit_DHT.AM2302
}

_sensor_type, _sensor_pin = None, None

def init(sensor_type, sensor_pin):
    _sensor_type = sensor_types[sensor_type]
    _sensor_pin = sensor_pin

def read():
    #Adafruit_DHT.read(DHT_TYPE, DHT_PIN)
    return (70,27)

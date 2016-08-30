import time
from porc import Client
from datetime import datetime
import RPi.GPIO as io
import json
import logging

# Initialize logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load application config file
logger.info('Loading configuration...')
with open('config.json', 'r') as f:
    config = json.load(f)

# Initialize state from config settings
logger.debug('Initializing state...')
sensor_types = { '11': Adafruit_DHT.DHT11,
                '22': Adafruit_DHT.DHT22,
                '2302': Adafruit_DHT.AM2302
}
sensor = sensor_types[config['sensor.type']]
pin = config['sensor.pinNum']
api_key = config['orchestrate.apiKey']
threshold = config['tempShutoffThreshold']
power_pin = config['heat.powerControlPinNum']
logger.info('Configuration loaded')

# Initialize power control port for our heating unit
logger.info('Initializing power...')
io.setmode(io.BCM)
io.setup(power_pin, io.OUT)
io.output(power_pin, False) # default turn off
logger.info('Power initialized')

# create a client using the default AWS US East host: https://api.orchestrate.io
logger.info('Initializing database connection...')
client = Client(api_key)
# make sure our API key works
logger.info('Testing database connection...')
client.ping().raise_for_status()
logger.info('Database connection complete')

def do_main_program():
    logger.debug('Running...')
    while True:
        logger.debug('Reading temp,humidity...')
        humidity, temp = read_sensor()
        logger.debug('Temp[%s] Humidity[%s]', temp, humidity)

        # Turn the heat off if we hit threshold temp, on otherwise
        if(temp > threshold):
            heat_off()
        else:
            heat_on()

        #log_to_db(humidity, temp)

        time.sleep(10)

def heat_on():
    loggder.debug('HEAT ON')
    switch(power_pin, True)

def heat_off():
    loggder.debug('HEAT OFF')
    switch(power_pin, False)

def read_sensor():
    #Adafruit_DHT.read(DHT_TYPE, DHT_PIN)
    70,27

def log_to_db(humidity, temp):
    response = client.post('picubator', {
      "humidity": humidity,
      "temp": temp,
      "timestamp": datetime.now()
    })
    # TODO: Log result of the db write

def switch(pin, mode):
    logger.debug('Setting pin %s to %s', pin, mode)
    io.output(pin, mode)

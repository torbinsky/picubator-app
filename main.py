import time

from porc import Client
from datetime import datetime
import RPi.GPIO as io

if len(sys.argv) == 6:
    sensor = sensor_args[sys.argv[1]]
    pin = sys.argv[2]
    api_key = sys.argv[3]
    threshold = sys.argv[4]
    power
else:
    print('usage: sudo ./main.py SENSOR GPIO_PIN_NUM ORCHESTRATE_KEY TEMP_THRESHOLD OUTPUT_COLLECTION')
    sys.exit(1)

# Initialize power control port
power_pin = 23

io.setmode(io.BCM)
io.setup(power_pin, io.OUT)


# create a client using the default AWS US East host: https://api.orchestrate.io
client = Client(api_key)

# make sure our API key works
client.ping().raise_for_status()

def do_main_program():
    while True:
        humidity, temp = read_sensor()

        # Turn the light off if we hit threshold temp, on otherwise
        if(temp > threshold):
            light_off()
        else:
            light_on()

        #log_to_db(humidity, temp)
        print "READING: "
        print humidity
        print temp
        print "\n"

        time.sleep(10)

def light_on():
    print "LIGHT ON\n"
    switch(power_pin, True)

def light_off():
    print "LIGHT OFF\n"
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

def switch(pin, mode):
    io.output(pin, mode)

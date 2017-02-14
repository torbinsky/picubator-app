import logging

from io import BytesIO
try:
    from picamera import PiCamera
except:
    print(
    '-------------------------------------------------------------------------')
    print(
    ' WARNING: Unable to import PiCamera library.')
    print(
    '-------------------------------------------------------------------------')
    
import base64

# Initialize logging
logger = logging.getLogger(__name__)

class Camera:
    'Represents a camera which will take stills'

    def __init__(self, x_res, y_res, light, cam_api = None):
        self.cam_api = cam_api or PiCamera()
        self.cam_api.resolution = (x_res, y_res)
        self.light = light

        logger.info('Camera initalized at resolution %sx%s', x_res, y_res)

    def capture_base64(self):
        # Remember the light's original state
        # TW: This will be an issue if things become concurrent
        lightWasOff = self.light.isOn()
        
        # Safely turn the light on and take a picture
        try:
            # Turn on the light
            self.light.on()
            
            # Byte stream for camera capture
            img_stream = BytesIO()
            logger.debug('Capturing image...')
            self.cam_api.capture(img_stream, format='jpeg')
        except:
            # Turn the light back off, if it was already off
            if(lightWasOff):
                self.light.off()
        
        # bytes into an array
        img_stream.seek(0)
        img_buf = img_stream.read()
        
        # cleanup resources
        img_stream.close()

        return base64.b64encode(img_buf)

    def __del__(self):
        logger.debug("Finished")

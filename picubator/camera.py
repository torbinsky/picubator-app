import logging

from io import BytesIO
from picamera import PiCamera
import base64

# Initialize logging
logger = logging.getLogger(__name__)

class Camera:
    'Represents a camera which will take stills'

    def __init__(self, x_res, y_res):
        self.cam_api = PiCamera()
        self.cam_api.resolution = (x_res, y_res)

        logger.info('Camera initalized at resolution %sx%s', x_res, y_res)

    def capture_base64():
        # Byte stream for camera capture
        img_stream = BytesIO()
        self.cam_api.capture(img_stream, format='jpeg')
        img_stream.seek(0)

        # bytes into an array
        img_buf = img_stream.read()
        # cleanup resources
        img_stream.close()

        return base64.b64encode(img_buf)

    def __del__(self):
        logger.debug("Cleaning up GPIO state")

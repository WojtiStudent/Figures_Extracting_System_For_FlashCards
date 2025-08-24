import os
from PIL import Image
import logging

logger = logging.getLogger(__name__)

DOCUMENT_INTELLIGENCE_LIMIT = 1024 * 1024 * 10

class ImageSizeReducer:
    def __init__(self, start_quality=95, max_size=DOCUMENT_INTELLIGENCE_LIMIT):
        logger.debug("""Initializing ImageSizeReducer with parameters: 
        start_quality: %s, 
        max_size: %s""", start_quality, max_size)
        self.max_size = max_size
        self.start_quality = start_quality

    def resize_image(self, image_path):
        logger.info("Resizing image: %s", image_path)
        current_size = os.stat(image_path).st_size
        if current_size < self.max_size:
            logger.info("Image is already smaller than max size: %s", current_size)
            return image_path
        quality = self.start_quality
        image = Image.open(image_path)
        while current_size >= self.max_size:
            logger.info("Resizing image to %s", quality)
            image.save(image_path, optimize=True, quality=quality)
            current_size = os.stat(image_path).st_size
            quality -= 1
        logger.info("Resized image to %s. Final quality: %s", current_size, quality)
        return image_path
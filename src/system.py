import os
import logging
from dotenv import load_dotenv

from src.components.figure_extractor import FigureExtractor
from src.components.image_size_reducer import ImageSizeReducer
from src.components.filename_generator import FilenameGenerator
from src.components.save_handler import SaveHandler

logger = logging.getLogger(__name__)

class System:
    def __init__(self, endpoint, key, model, output_folder):
        logger.debug("""Initializing System with parameters: 
        endpoint: %s, 
        key: %s, 
        model: %s, 
        output_folder: %s""", endpoint, key, model, output_folder)
        self.image_size_reducer = ImageSizeReducer()

        self.figure_extractor = FigureExtractor(
            endpoint=endpoint,
            key=key
        )
        self.filename_generator = FilenameGenerator(model)
        self.save_handler = SaveHandler(output_folder)

    def run_single_image(self, image_path):
        logger.info("Running system for image: %s", image_path)
        self.image_size_reducer.resize_image(image_path)
        figures = self.figure_extractor.extract_figures(image_path)
        for figure in figures:
            filename = self.filename_generator.generate_filename(image=figure)
            self.save_handler.save_figure(figure, image_path, filename)
        return filename, figures

    def run_folder(self, folder_path):
        logger.info("Running system for folder: %s", folder_path)
        for i, file in enumerate(os.listdir(folder_path)):
            logger.info("Running system for file %s of %s", i + 1, len(os.listdir(folder_path)))
            if file.endswith(".jpg") or file.endswith(".png") or file.endswith(".jpeg") or file.endswith(".jfif"):
                self.run_single_image(os.path.join(folder_path, file))






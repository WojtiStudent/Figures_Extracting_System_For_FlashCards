import os
import logging

logger = logging.getLogger(__name__)


class SaveHandler:
    def __init__(self, output_folder):
        logger.debug("""Initializing SaveHandler with parameters: 
        output_folder: %s""", output_folder)
        self.output_folder = output_folder

    def save_figure(self, figure, source_image_path, generated_filename):
        logger.debug("""Saving figure with parameters: 
        figure: %s, 
        source_image_path: %s, 
        generated_filename: %s""", figure, source_image_path, generated_filename)
        logger.info("Saving figure with filename: %s from source image: %s", generated_filename, source_image_path)
        
        source_image_filename = os.path.basename(source_image_path)
        logger.debug("Source image filename: %s", source_image_filename)

        os.makedirs(self.output_folder, exist_ok=True)
        
        dirs_in_output_folder = os.listdir(self.output_folder)
        logger.debug("Dirs in output folder: %s", dirs_in_output_folder)
        if source_image_filename not in dirs_in_output_folder:
            os.makedirs(os.path.join(self.output_folder, source_image_filename))

        # try save file
        files_in_source_image_folder = os.listdir(os.path.join(self.output_folder, source_image_filename))
        final_dir_path = os.path.join(self.output_folder, source_image_filename)
        filename = f"{generated_filename}.jpg"
        duplicate_counter = 0

        while filename in files_in_source_image_folder:
            logger.debug("Filename %s already exists in source image folder. Incrementing duplicate counter.", filename)
            duplicate_counter += 1
            filename = f"{generated_filename}_{duplicate_counter}.jpg"

        logger.debug("Saving figure to %s", os.path.join(final_dir_path, filename))
        figure.save(os.path.join(final_dir_path, filename))
        logger.info("Saved figure to %s", os.path.join(final_dir_path, filename))

from azure.ai.documentintelligence import DocumentIntelligenceClient
from azure.core.credentials import AzureKeyCredential
from PIL import Image, ImageOps
import base64
import logging

from src.components.bounding_box import BoundingBox, BoundingBoxType

logger = logging.getLogger(__name__)


class FigureExtractor:

    def __init__(self, endpoint, key, text_height_multiplier=3):
        logger.debug("""Initializing FigureExtractor with parameters: 
        endpoint: %s, 
        key: %s, 
        text_height_multiplier: %s""", endpoint, key, text_height_multiplier)
        self.endpoint = endpoint
        self.key = key
        self.document_intelligence_client = DocumentIntelligenceClient(
            endpoint=self.endpoint, credential=AzureKeyCredential(self.key)
        )
        self.text_height_multiplier = text_height_multiplier

    @staticmethod
    def encode_image(image_path):
        logger.debug("Encoding image: %s", image_path)
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode("utf-8")

    def get_result(self, image_path):
        logger.debug("Getting result for image: %s", image_path)
        base64_image = self.encode_image(image_path)
        poller = self.document_intelligence_client.begin_analyze_document(
            "prebuilt-layout", {"base64Source": base64_image}
        )
        result = poller.result()
        logger.debug("Result: %s", result)
        return result

    @staticmethod
    def read_image(image_path):
        logger.debug("Reading image: %s", image_path)
        image = Image.open(image_path)
        image = ImageOps.exif_transpose(image)
        logger.debug("Image: %s", image)
        return image

    @staticmethod
    def get_figures(result, angle, old_image_size, new_image_size):
        logger.debug("""Getting figures with parameters: 
        angle: %s, 
        old_image_size: %s, 
        new_image_size: %s""", angle, old_image_size, new_image_size)
        figures = []
        for figure in result.figures:
            figure = BoundingBox(figure["boundingRegions"][0]["polygon"], BoundingBoxType.FIGURE, angle, old_image_size, new_image_size)
            figures.append(figure)
        logger.debug("Figures: %s", figures)
        return figures

    @staticmethod
    def get_paragraphs(result, angle, old_image_size, new_image_size):
        logger.debug("""Getting paragraphs with parameters: 
        angle: %s, 
        old_image_size: %s, 
        new_image_size: %s""", angle, old_image_size, new_image_size)
        paragraphs = []
        for paragraph in result.paragraphs:
            paragraph = BoundingBox(paragraph["boundingRegions"][0]["polygon"], BoundingBoxType.PARAGRAPH, angle, old_image_size, new_image_size)
            paragraphs.append(paragraph)
        logger.debug("Paragraphs: %s", paragraphs)
        return paragraphs

    @staticmethod
    def get_line_height(result, angle, old_image_size, new_image_size):
        logger.debug("""Getting line height with parameters: 
        angle: %s, 
        old_image_size: %s, 
        new_image_size: %s""", angle, old_image_size, new_image_size)
        line_height = float('inf')
        for line in result.pages[0].lines:
            line = BoundingBox(line["polygon"], BoundingBoxType.LINE, angle, old_image_size, new_image_size)
            line_height = min(line_height, line.bottom - line.top)
        if line_height == float('inf'):
            line_height = 10
        return line_height

    @staticmethod
    def cut_off_figure_from_image(image, figure):
        logger.debug("""Cutting off figure from image: 
        figure: %s""", figure)
        return image.crop((figure.left, figure.top, figure.right, figure.bottom))


    def extract_figures(self, image_path):
        logger.info("Extracting figures from image: %s", image_path)
        result = self.get_result(image_path)
        angle = result.pages[0].angle
        image = self.read_image(image_path)
        rotated_image = image.rotate(angle, expand=True)

        figures = self.get_figures(result, angle, image.size, rotated_image.size)
        logger.info("Found %s figures", len(figures))
        paragraphs = self.get_paragraphs(result, angle, image.size, rotated_image.size)
        line_height = self.get_line_height(result, angle, image.size, rotated_image.size)
        logger.info("Determined line height: %s", line_height)
        extended_figures = []
        for i, figure in enumerate(figures):
            logger.info("Extending figure %s of %s", i + 1, len(figures))
            figure = BoundingBox.extend_bounding_box(figure, line_height * self.text_height_multiplier)
            overlapping_paragraphs = [p for p in paragraphs if BoundingBox.check_if_bounding_boxes_overlap(figure, p)]
            extended_figure = BoundingBox.extend_figure_bounding_box(figure, overlapping_paragraphs)
            extended_figures.append(extended_figure)

        cropped_images = []
        for i, figure in enumerate(extended_figures):
            logger.info("Cropping figure %s of %s", i + 1, len(extended_figures))
            cropped_image = self.cut_off_figure_from_image(rotated_image, figure)
            cropped_images.append(cropped_image)

        logger.info("Finished extracting figures")
        return cropped_images
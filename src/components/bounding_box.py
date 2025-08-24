from enum import Enum
import numpy as np
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)

class BoundingBoxType(Enum):
    FIGURE = "figure"
    PARAGRAPH = "paragraph"
    LINE = "line"

@dataclass
class BoundingBox:
    type: BoundingBoxType
    bounding_box: list[float]
    left: float
    top: float
    right: float
    bottom: float

    def __init__(self, bounding_box, type: BoundingBoxType, angle, old_image_size, new_image_size):
        logger.debug("""Creating bounding box with parameters: 
        angle: %s, 
        old_image_size: %s, 
        new_image_size: %s, 
        bounding_box: %s""",
        angle, old_image_size, new_image_size, bounding_box)
        self.type = type
        points = np.array(bounding_box).reshape(4, 2)
        rotated_points = self.rotate_points(points, angle, old_image_size, new_image_size)
        self.bounding_box = rotated_points.flatten()
        # PIL params
        self.left, self.top, self.right, self.bottom = self.transform_bounding_box(self.bounding_box)

    @staticmethod
    def transform_bounding_box(bounding_box):
        logger.debug("Transforming bounding box: %s", bounding_box)
        left = min(bounding_box[0], bounding_box[6])
        top = min(bounding_box[1], bounding_box[3])
        right = max(bounding_box[2], bounding_box[4])
        bottom = max(bounding_box[5], bounding_box[7])
        logger.debug("""Transformed bounding box: 
        left: %s, 
        top: %s, 
        right: %s, 
        bottom: %s""", left, top, right, bottom)
        return left, top, right, bottom

    @staticmethod
    def check_if_bounding_boxes_overlap(bounding_box1, bounding_box2):
        logger.debug("""Checking if bounding boxes overlap: 
        bounding_box1: %s, 
        bounding_box2: %s""", 
        bounding_box1, bounding_box2)
        return (
            bounding_box2.top<=bounding_box1.top<=bounding_box2.bottom or bounding_box1.top<=bounding_box2.top<=bounding_box1.bottom) and (
            bounding_box2.left<=bounding_box1.left<=bounding_box2.right or bounding_box1.left<=bounding_box2.left<=bounding_box1.right)

    @staticmethod
    def extend_bounding_box(bounding_box, value):
        logger.debug("""Extending bounding box: 
        bounding_box: %s, 
        value: %s""", bounding_box, value)
        bounding_box.left -= value
        bounding_box.right += value
        bounding_box.top -= value
        bounding_box.bottom += value
        logger.debug("Extended bounding box: %s", bounding_box)
        return bounding_box

    @staticmethod
    def extend_figure_bounding_box(figure_bounding_box, overlapping_paragraph_bounding_boxes):
        logger.debug("""Extending figure bounding box: 
        figure_bounding_box: %s,
        n_overlapping_paragraphs: %s,
        overlapping_paragraph_bounding_boxes: %s""", 
        figure_bounding_box, len(overlapping_paragraph_bounding_boxes), overlapping_paragraph_bounding_boxes)
        if figure_bounding_box.type != BoundingBoxType.FIGURE:
            raise ValueError("Figure bounding box must be of type FIGURE")
        if not all(b.type == BoundingBoxType.PARAGRAPH for b in overlapping_paragraph_bounding_boxes):
            raise ValueError("All text bounding boxes must be of type PARAGRAPH")

        logger.info("Found %s paragraphs overlapping with figure", len(overlapping_paragraph_bounding_boxes))
        for paragraph_bounding_box in overlapping_paragraph_bounding_boxes:
            figure_bounding_box.top = min(figure_bounding_box.top, paragraph_bounding_box.top)
            figure_bounding_box.bottom = max(figure_bounding_box.bottom, paragraph_bounding_box.bottom)
            figure_bounding_box.left = min(figure_bounding_box.left, paragraph_bounding_box.left)
            figure_bounding_box.right = max(figure_bounding_box.right, paragraph_bounding_box.right)
        logger.debug("Extended figure bounding box: %s", figure_bounding_box)

        return figure_bounding_box

    @staticmethod
    def rotate_points(points, angle, old_image_size, new_image_size):
        logger.debug("""Rotating points: 
        points: %s, 
        angle: %s, 
        old_image_size: %s, 
        new_image_size: %s""", points, angle, old_image_size, new_image_size)
        def rotate(p, degrees=0):
            angle = np.deg2rad(degrees)
            R = np.array([[np.cos(-angle), -np.sin(-angle)],
                        [np.sin(-angle),  np.cos(-angle)]])
            result = (R @ p.T).T
            return result
        center = (old_image_size[0]/2, old_image_size[1]/2)
        points = points - center
        points = rotate(points, degrees=angle)
        points = points + center
        bias = np.array([(new_image_size[0] - old_image_size[0])//2, (new_image_size[1] - old_image_size[1])//2])
        points = points + bias
        logger.debug("Rotated points: %s", points)
        return points
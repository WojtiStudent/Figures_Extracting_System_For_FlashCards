import base64
from openai import OpenAI
from io import BytesIO
import logging

logger = logging.getLogger(__name__)

CHAR_LIMIT = 60

class FilenameGenerator:
    prompt = """
Otrzymasz zdjęcie strony z Vademecuum Biologicznego. Strona zawiera tekst oraz przede wszystkim ilustrację.

Nazwij ilustrację obecną na zdjęciu, bądź jak najbardziej zwięzły - wytworzona nazwa ma być nazwą pliku pozwalającą szybko namierzyć odpowiednią grafikę w obrębie jednego działu. 
Użyj maksymalnie 5 słów. Zwróć tylko nazwę, bez żadnych dodatkowych informacji, a spacje zamień na podkreślenie.

Przykłady: 
Enzymy_aktywowane_przez_fosforylację
Fotosystem
Cykl_Krebsa
"""
    def __init__(self, model):
        logger.debug("""Initializing FilenameGenerator with parameters: 
        model: %s""", model)
        self.client = OpenAI()
        self.model = model

    @staticmethod
    def encode_image_file(image_path):
        logger.debug("Encoding image file: %s", image_path)
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode("utf-8")

    @staticmethod
    def encode_PIL_image(image):
        logger.debug("Encoding PIL image")
        with BytesIO() as output:
            image.save(output, format="JPEG")
            return base64.b64encode(output.getvalue()).decode("utf-8")

    
    def generate_filename(self, image_path = None, image = None):
        logger.info("Generating filename")
        logger.debug("""Generating filename with parameters: 
        image_path: %s, 
        image: %s""", image_path, image)
        if image_path is not None:
            base64_image = self.encode_image_file(image_path)
        elif image is not None:
            base64_image = self.encode_PIL_image(image)
        else:
            raise ValueError("Either image_path or image must be provided")

        response = self.client.responses.create(
            model=self.model,
            input=[
                {
                    "role": "user",
                    "content": [
                        { "type": "input_text", "text": self.prompt },
                        {
                            "type": "input_image",
                            "image_url": f"data:image/jpeg;base64,{base64_image}",
                        },
                    ],
                }
            ]
        )

        logger.info("Generated filename: %s", response.output_text)
        return response.output_text.strip()[:CHAR_LIMIT]

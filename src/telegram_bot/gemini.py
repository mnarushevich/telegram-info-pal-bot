"""Gemini API client."""

import logging
from io import BytesIO
from PIL import Image

from google import genai

logger = logging.getLogger(__name__)

class GeminiClient:
    """Gemini API client."""

    def __init__(self, api_key: str | None):
        """Initialize the Gemini client."""
        if api_key is None:
            raise ValueError("Gemini API key is required but not provided")
        self.client = genai.Client(api_key=api_key)

    async def generate_content(self, prompt: str, filename: str = "myimage.png") -> bool:
        """Generate content using Gemini API.
        
        Args:
            prompt: The text prompt for image generation.
            filename: The filename to save the generated image.
            
        Returns:
            bool: True if image generation and saving was successful, False otherwise.
        """
        try:
            response = self.client.models.generate_content(
                model="gemini-2.5-flash-image-preview",
                contents=[prompt]
            )

            image_saved = False
            for part in response.candidates[0].content.parts:
                if part.inline_data is not None:
                    # Convert the raw data into an image
                    image = Image.open(BytesIO(part.inline_data.data))
                    # Save it as a PNG file
                    #TODO: Switch to S3 storage
                    image.save(filename)
                    image_saved = True
                    break

            if image_saved:
                logger.info("Image saved to %s", filename)
                return True
            else:
                logger.warning("No image data found in response")
                return False
                
        except Exception as e:
            logger.error("Error generating image: %s", e)
            return False
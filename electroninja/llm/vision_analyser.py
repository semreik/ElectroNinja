# electroninja/llm/vision_analyser.py
import os
import logging
import base64
import openai
from electroninja.config.settings import Config
from electroninja.llm.prompts.circuit_prompts import VISION_IMAGE_ANALYSIS_PROMPT

logger = logging.getLogger('electroninja')

class VisionAnalyzer:
    """Analyzes circuit images using OpenAI's vision model"""
    
    def __init__(self, config=None):
        self.config = config or Config()
        self.model = self.config.OPENAI_VISION_MODEL  # Should be "gpt-4o"
        openai.api_key = self.config.OPENAI_API_KEY
        logger.info(f"Vision Analyzer initialized with OpenAI model: {self.model}")
        
    def analyze_circuit_image(self, image_path, prompt):
        """
        Analyze a circuit image to determine if it satisfies the circuit description.
        
        Args:
            image_path (str): Path to the circuit image.
            circuit_description (str): The circuit description loaded from file.
            
        Returns:
            str: 'Y' if the circuit is verified, or detailed feedback if not.
        """
        try:
            logger.info(f"Starting analysis of circuit image: {image_path}")
            
            if not os.path.exists(image_path):
                error_msg = f"Image file not found: {image_path}"
                logger.error(error_msg)
                return f"Error: {error_msg}"
            
            # Log file size
            file_size = os.path.getsize(image_path)
            logger.info(f"Image file size: {file_size} bytes")
                
            # Encode image
            with open(image_path, "rb") as image_file:
                image_data = base64.b64encode(image_file.read()).decode('utf-8')
                logger.info(f"Successfully encoded image data (length: {len(image_data)})")
                
            logger.info("Sending prompt to OpenAI vision model...")
            
            # Call OpenAI API with both text and the image data
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/png;base64,{image_data}",
                                    "detail": "high",
                                }
                            }
                        ]
                    }
                ]
            )
            
            # Extract and process analysis
            analysis = response.choices[0].message.content.strip()
            is_verified = analysis == 'Y'
            verification_status = "VERIFIED" if is_verified else "NOT VERIFIED"
            logger.info(f"Vision analysis complete: Circuit {verification_status}")
            
            return analysis
            
        except Exception as e:
            error_msg = f"Vision analysis error: {str(e)}"
            logger.error(error_msg)
            return f"Error: {error_msg}"
        
    def produce_description_of_image(self, image_path, prompt):
        """
        Look at the circuit image and produce a description of it.

        Args:
            image_path (str): Path to the circuit image.
            prompt (str): The prompt to analyze the image and produce the description.

        Returns:
            str: DESC=<the description of the image>
        """
        try:
            logger.info(f"Starting description of circuit image: {image_path}")

            if not os.path.exists(image_path):
                error_msg = f"Image file not found: {image_path}"
                logger.error(error_msg)
                return f"Error: {error_msg}"

            # Log file size
            file_size = os.path.getsize(image_path)
            logger.info(f"Image file size: {file_size} bytes")

            # Encode image
            with open(image_path, "rb") as image_file:
                image_data = base64.b64encode(image_file.read()).decode("utf-8")
                logger.info(f"Successfully encoded image data (length: {len(image_data)})")

            logger.info("Sending prompt to OpenAI vision model...")

            # Define system prompt
            system_prompt = {
                "role": "system",
                "content": (
                    "You are a highly reliable and detail-oriented circuit analysis expert. "
                    "You always reason step-by-step before making a final judgment. "
                    "You base circuit interpretation strictly on electrical node connections, not layout or orientation. "
                    "Be careful: parallel components may be aligned horizontally. "
                    "Only describe what is factual from the image and return a description that begins with 'DESC='."
                )
            }

            # Call OpenAI API
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[
                    system_prompt,
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/png;base64,{image_data}",
                                    "detail": "high",
                                }
                            }
                        ]
                    }
                ]
            )

            # Extract and process analysis
            output = response.choices[0].message.content.strip()

            description = output.split('DESC=')[1].strip()

            return description

        except Exception as e:
            error_msg = f"Vision analysis error: {str(e)}"
            logger.error(error_msg)
            return f"Error: {error_msg}"

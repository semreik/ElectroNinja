# electroninja/backend/vision_processor.py
import logging
import os
from electroninja.config.settings import Config
from electroninja.llm.vision_analyser import VisionAnalyzer
from electroninja.llm.prompts.circuit_prompts import VISION_IMAGE_ANALYSIS_PROMPT
from electroninja.llm.prompts.button_prompts import COMPILE_CODE_DESC_PROMPT


logger = logging.getLogger('electroninja')

class VisionProcessor:
    """
    Processes circuit images with the vision model to evaluate correctness.
    """
    def __init__(self, config: Config = None):
        self.config = config or Config()
        self.vision_analyzer = VisionAnalyzer(self.config)
        self.logger = logger

    def analyze_circuit_image(self, prompt_id: int, iteration: int) -> str:
        """
        Analyzes the circuit image against the saved circuit description for the given prompt and iteration.
        
        Args:
            prompt_id (int): Identifier for the current prompt session.
            iteration (int): The iteration number (used to locate the image file).
            
        Returns:
            str: 'Y' if the circuit is verified, or an analytical explanation if not.
        """
        # Build the image path based on prompt_id and iteration
        image_path = os.path.join("data", "output", f"prompt{prompt_id}", f"output{iteration}", "image.png")
        self.logger.info(f"Analyzing circuit image from: '{image_path}' for prompt ID: {prompt_id}, iteration: {iteration}")
        
        # Load the circuit description from file
        description_path = os.path.join("data", "output", f"prompt{prompt_id}", "description.txt")
        if not os.path.exists(description_path):
            error_msg = f"Description file not found: {description_path}"
            self.logger.error(error_msg)
            print(error_msg)
            return f"Error: {error_msg}"
        
        with open(description_path, "r", encoding="utf-8") as f:
            circuit_description = f.read().strip()
        
        # Print input information for debugging
        print(f"\n{'='*80}\nVISION PROCESSOR INPUT:\n{'='*80}")
        print(f"Image path: {image_path}")
        print(f"Circuit description (first 200 chars):\n{circuit_description[:200]}...")
        if os.path.exists(image_path):
            file_size = os.path.getsize(image_path)
            print(f"Image exists: Yes (Size: {file_size} bytes)")
        else:
            print("Image exists: No")
        print('='*80)


        prompt = VISION_IMAGE_ANALYSIS_PROMPT.format(description=circuit_description)
        
        # Analyze the image using the circuit description as context
        analysis = self.vision_analyzer.analyze_circuit_image(image_path, prompt=prompt)
        
        # Print and log the analysis result
        is_correct = analysis == 'Y'
        print(f"\n{'='*80}\nVISION PROCESSOR OUTPUT:\n{'='*80}")
        print(f"Analysis result: {analysis}")
        print(f"Circuit verified as correct: {is_correct}")
        print('='*80)
        
        self.logger.info(f"Circuit analysis complete. Correct: {is_correct}")
        return analysis

    def is_circuit_verified(self, vision_feedback: str) -> bool:
        return vision_feedback.strip() == 'Y'
    

    def create_description_from_compile(self, prompt_id: int):
        """
        Creates a circuit description from the compiled circuit image.
        
        Args:
            prompt_id (int): Identifier for the current prompt session.
            
        Returns:
            str: The generated circuit description.
        """
        # Load the circuit image
        image_path = os.path.join("data", "output", f"prompt{prompt_id}", "output0", "image.png")
        if not os.path.exists(image_path):
            error_msg = f"Image file not found: {image_path}"
            self.logger.error(error_msg)
            return f"Error: {error_msg}"
        
        prompt = COMPILE_CODE_DESC_PROMPT
        
        # Create a description using the vision model
        description = self.vision_analyzer.produce_description_of_image(image_path, prompt)
        
        # Save the description to a file
        description_path = os.path.join("data", "output", f"prompt{prompt_id}", "description.txt")
        with open(description_path, "w", encoding="utf-8") as f:
            f.write(description)
        
        self.logger.info(f"Created and saved circuit description from image: {description_path}")
        return description

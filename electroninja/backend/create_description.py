import logging
import os
from electroninja.llm.providers.openai import OpenAIProvider

logger = logging.getLogger('electroninja')

class CreateDescription:
    """
    Creates a circuit description using the OpenAI provider.
    """
    def __init__(self, openai_provider: OpenAIProvider):
        self.provider = openai_provider
        self.logger = logger

    def create_description(self, previous_description: str, new_request: str) -> str:
        """
        Creates a circuit description by merging a previous description with a new modification request.
        """
        self.logger.info(f"Creating description from: previous='{previous_description}', new='{new_request}'")
        
        description = self.provider.create_description(previous_description, new_request)
        
        self.logger.info(f"Generated circuit description: '{description}'")
        
        return description
        
    def save_description(self, description: str, prompt_id: int) -> str:
        """
        Saves the circuit description to a file in the output/prompt<n> directory.
        Returns the path to the saved file.
        """
        output_dir = os.path.join("data", "output", f"prompt{prompt_id}")
        os.makedirs(output_dir, exist_ok=True)
        
        description_path = os.path.join(output_dir, "description.txt")
        with open(description_path, "w", encoding="utf-8") as f:
            f.write(description)
            
        self.logger.info(f"Saved circuit description to: {description_path}")
        return description_path

    def load_description(self, prompt_id: int) -> str:
        """
        Loads the circuit description from a file in the output/prompt<n> directory.
        Returns None if the file doesn't exist.
        """
        description_path = os.path.join("data", "output", f"prompt{prompt_id}", "description.txt")
        
        if not os.path.exists(description_path):
            self.logger.info(f"No previous description found at: {description_path}")
            return None
            
        try:
            with open(description_path, "r", encoding="utf-8") as f:
                description = f.read()
            self.logger.info(f"Loaded circuit description from: {description_path}")
            return description
        except Exception as e:
            self.logger.error(f"Error loading description: {str(e)}")
            return None

import logging
import os
from electroninja.llm.providers.openai import OpenAIProvider

logger = logging.getLogger('electroninja')

class RequestEvaluator:
    """
    Evaluates whether a user request is related to electrical circuits using the OpenAI provider.
    Also handles saving and loading the evaluation components (e.g., component letters) for each prompt.
    """
    def __init__(self, openai_provider: OpenAIProvider):
        self.provider = openai_provider
        self.logger = logger

    def evaluate_request(self, prompt: str, prompt_id: int) -> str:
        """
        Evaluates a user request. If the request is circuit-related, the model returns component letters 
        (e.g., "R, C"). Otherwise, it returns 'N'. If the result is not 'N', the components are saved 
        to data/output/prompt{prompt_id}/components.txt.
        
        Args:
            prompt (str): The user's request.
            prompt_id (int): The identifier for the current prompt/session.
        
        Returns:
            str: The raw evaluation result.
        """
        self.logger.info(f"Evaluating request: {prompt}")
        print(f"\n{'='*80}\nEVALUATOR PROMPT INPUT:\n{'='*80}\n{prompt}\n{'='*80}")
        
        result = self.provider.evaluate_circuit_request(prompt)
        
        print(f"\n{'='*80}\nEVALUATOR RESULT OUTPUT:\n{'='*80}\n{result}\n{'='*80}")
        self.logger.info(f"Evaluation result: {result}")
        
        if result.strip().upper() != 'N':
            self.save_components(result, prompt_id)
        
        return result

    # Alias to support legacy pipeline calls.
    def is_circuit_related(self, prompt: str) -> str:
        return self.evaluate_request(prompt, prompt_id=1)  # Default prompt_id can be overridden externally.

    def save_components(self, components: str, prompt_id: int) -> str:
        """
        Saves the evaluation result (component letters) to data/output/prompt{prompt_id}/components.txt.
        
        Args:
            components (str): The evaluation output (e.g., "R, C").
            prompt_id (int): The current prompt/session identifier.
        
        Returns:
            str: The file path to the saved components file.
        """
        if components.strip().upper() == 'N':
            self.logger.info("Evaluation result is 'N'; nothing to save.")
            return None

        output_dir = os.path.join("data", "output", f"prompt{prompt_id}")
        os.makedirs(output_dir, exist_ok=True)
        file_path = os.path.join(output_dir, "components.txt")
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(components)
            self.logger.info(f"Components saved to {file_path}")
            return file_path
        except Exception as e:
            self.logger.error(f"Error saving components: {e}")
            return None

    def load_components(self, prompt_id: int) -> str:
        """
        Loads the evaluation components from data/output/prompt{prompt_id}/components.txt.
        
        Args:
            prompt_id (int): The prompt/session identifier.
        
        Returns:
            str: The loaded components string, or None if the file does not exist.
        """
        file_path = os.path.join("data", "output", f"prompt{prompt_id}", "components.txt")
        if not os.path.exists(file_path):
            self.logger.info(f"Components file not found: {file_path}")
            return None
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = f.read().strip()
            self.logger.info(f"Components loaded from {file_path}")
            return data
        except Exception as e:
            self.logger.error(f"Error loading components: {e}")
            return None

    def merge_components(self, new_components: str, previous_prompt_id: int, current_prompt_id: int) -> str:
        """
        Merges the new evaluation result with the components from the previous prompt
        by concatenating the previous components with the new ones.
        If new_components is 'N', returns "N".
        """
        if new_components.strip().upper() == 'N':
            self.logger.info("New evaluation result is 'N'; no components to merge.")
            return "N"

        # Load previous components from the previous prompt folder.
        prev_components = self.load_components(previous_prompt_id)
        
        # Concatenate: if previous components exist, append new components.
        if prev_components:
            merged_components = prev_components.strip() + ", " + new_components.strip()
        else:
            merged_components = new_components.strip()

        # Save the merged components into the current prompt folder.
        output_dir = os.path.join("data", "output", f"prompt{current_prompt_id}")
        os.makedirs(output_dir, exist_ok=True)
        file_path = os.path.join(output_dir, "components.txt")
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(merged_components)
            self.logger.info(f"Merged components saved to {file_path}")
        except Exception as e:
            self.logger.error(f"Error saving merged components: {e}")
        return merged_components
    
    def list_components(self, prompt_id: int) -> str:
        """
        Lists the components based on the code in the file in data/output/prompt{prompt_id}/output0/code.asc
        
        Args:
            prompt_id (int): The prompt/session identifier.
        
        Returns:
            str: The components string, or None if the file does not exist.
        """
        asc_path = os.path.join("data", "output", f"prompt{prompt_id}", "output0", "code.asc")
        if not os.path.exists(asc_path):
            self.logger.info(f"ASC file not found: {asc_path}")
            return None
        
        output_dir = os.path.join("data", "output", f"prompt{prompt_id}")
        os.makedirs(output_dir, exist_ok=True)
        file_path = os.path.join(output_dir, "components.txt")
        
        try:
            with open(asc_path, "r", encoding="utf-8") as f:
                asc_code = f.read()
            components = self.provider.list_components(asc_code)
            self.logger.info(f"Components extracted from {asc_path}: {components}")
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(components)
            self.logger.info(f"Components saved to {file_path}")
            return components
        except Exception as e:
            self.logger.error(f"Error extracting components from ASC: {e}")
            return None

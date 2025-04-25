import logging
from typing import List, Dict, Any
from electroninja.llm.providers.openai import OpenAIProvider
from electroninja.llm.vector_store import VectorStore

logger = logging.getLogger('electroninja')

class CircuitGenerator:
    """
    Generates and refines ASC code for circuit designs using the OpenAI provider.
    """
    def __init__(self, openai_provider: OpenAIProvider, vector_store: VectorStore):
        self.provider = openai_provider
        self.vector_store = vector_store
        self.logger = logger

    def _ensure_header(self, asc_code: str) -> str:
        """Ensure the ASC code contains the required header."""
        if not asc_code.startswith("Version 4"):
            asc_code = "Version 4\nSHEET 1 880 680\n" + asc_code
        return asc_code

    def generate_asc_code(self, description: str, prompt_id: int) -> str:
        """
        Generates ASC code by retrieving examples, building a comprehensive prompt (with instructions),
        and then asking the provider to generate the code.
        """
        self.logger.info(f"Generating ASC code for circuit description: '{description}'")
        
        # Retrieve similar examples from the vector store using the description
        examples = self.vector_store.search(description, top_k=3)

        # Generate ASC code using the provider, passing prompt_id to load components/instructions.
        asc_code = self.provider.generate_asc_code(description, examples, prompt_id)
        clean_asc = self.provider.extract_clean_asc_code(asc_code)
        final_asc = self._ensure_header(clean_asc)
        
        # Print output details (for debugging)
        print(f"\n{'='*80}\nCIRCUIT GENERATOR OUTPUT:\n{'='*80}")
        print(f"Original output length: {len(asc_code)} chars")
        print(f"Clean ASC code length: {len(clean_asc)} chars")
        print(f"Final ASC code (first 100 chars):\n{final_asc[:100]}...")
        print('='*80)
        
        self.logger.info("ASC code generated successfully")
        return final_asc

    # The refine_asc_code method remains unchanged.


    def refine_asc_code(self, prompt_id: int, iteration: int, vision_feedback: str) -> str:
        """
        Refines ASC code by using the new composite refinement prompt.
        
        Args:
            prompt_id (int): Identifier for the current prompt session.
            iteration (int): The iteration number corresponding to the incorrect ASC code.
            vision_feedback (str): The vision feedback to be included in the prompt.
        
        Returns:
            str: The refined, corrected ASC code.
        """
        self.logger.info(f"Refining ASC code for prompt ID: {prompt_id}, iteration: {iteration}")
        
        print(f"\n{'='*80}\nCIRCUIT REFINER PROMPT INPUT:\n{'='*80}")
        print(f"Using prompt ID: {prompt_id} and iteration: {iteration}")
        print(f"Vision feedback (first 200 chars):\n{vision_feedback[:200]}...")
        print('=' * 80)
        
        refined_asc = self.provider.refine_asc_code(prompt_id, iteration, vision_feedback)
        clean_asc = self.provider.extract_clean_asc_code(refined_asc)
        final_asc = self._ensure_header(clean_asc)
        
        print(f"\n{'='*80}\nCIRCUIT REFINER OUTPUT:\n{'='*80}")
        print(f"Original refined output length: {len(refined_asc)} chars")
        print(f"Clean ASC code length: {len(clean_asc)} chars")
        print(f"Final ASC code (first 100 chars):\n{final_asc[:100]}...")
        print('=' * 80)
        
        self.logger.info("ASC code refined successfully")
        return final_asc

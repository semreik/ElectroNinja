import os
import sys
import logging
import openai
from dotenv import load_dotenv

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from electroninja.config.settings import Config
from electroninja.llm.providers.openai import OpenAIProvider
from electroninja.llm.vector_store import VectorStore
from electroninja.backend.circuit_generator import CircuitGenerator

load_dotenv()
logging.basicConfig(level=logging.INFO)

def test_asc_code_refinement():
    """Test ASC code refinement based on vision feedback with raw LLM I/O printed."""
    print("\n====== TEST: ASC CODE REFINEMENT ======")
    
    config = Config()
    llm_provider = OpenAIProvider(config)
    vector_store = VectorStore(config)
    circuit_generator = CircuitGenerator(llm_provider, vector_store)
    
    # Set default prompt ID and iteration
    prompt_id = 1
    iteration = 0

    # Sample vision feedback for testing
    vision_feedback = (
        "1. The circuit does not correctly implement a low pass filter.\n"
        "   Replace the inductor with a capacitor to form an RC low pass filter.\n"
        "2. Expected: An RC low pass filter with the proper cutoff frequency."
    )
    
    # Set up a wrapper to intercept and print raw LLM input and output
    original_create = openai.ChatCompletion.create

    def create_wrapper(**kwargs):
        print("\n=== RAW INPUT TO LLM ===")
        for message in kwargs["messages"]:
            print(f"Role: {message['role']}")
            print("Content:")
            print(message['content'])
            print("-" * 50)
        response = original_create(**kwargs)
        print("\n=== RAW OUTPUT FROM LLM ===")
        print(response.choices[0].message.content)
        print("=" * 25)
        return response

    openai.ChatCompletion.create = create_wrapper

    try:
        # Call the refinement function with the given prompt ID, iteration, and vision feedback.
        refined_asc = circuit_generator.refine_asc_code(prompt_id, iteration, vision_feedback)
        print("\n=== REFINED ASC CODE ===")
        print(refined_asc)
    finally:
        openai.ChatCompletion.create = original_create
    
    return refined_asc

if __name__ == "__main__":
    test_asc_code_refinement()

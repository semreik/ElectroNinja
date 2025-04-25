import os
import sys
import logging
import openai
from dotenv import load_dotenv

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from electroninja.config.settings import Config
from electroninja.llm.providers.openai import OpenAIProvider
from electroninja.llm.vector_store import VectorStore
from electroninja.backend.circuit_generator import CircuitGenerator

# Load environment variables and set up logging
load_dotenv()
logging.basicConfig(level=logging.INFO)

prompt_id = 1  # Set the prompt ID for the test

def test_asc_generation_from_description():
    print("\n====== TEST: ASC GENERATION FROM DESCRIPTION ======")
    
    # Path to the saved description file for prompt1
    description_path = os.path.join("data", "output", f"prompt{prompt_id}", "description.txt")
    
    if not os.path.exists(description_path):
        print(f"Description file not found at: {description_path}")
        return
    
    # Load the circuit description from file using utf-8 encoding
    with open(description_path, "r", encoding="utf-8") as f:
        description = f.read().strip()
    
    print("\nLoaded Circuit Description:")
    print(description)
    
    # Initialize configuration, provider, vector store and CircuitGenerator
    config = Config()
    provider = OpenAIProvider(config)
    vector_store = VectorStore(config)
    vector_store.load()
    circuit_generator = CircuitGenerator(provider, vector_store)
    
    # Intercept OpenAI API calls to print raw input and output for debugging
    original_create = openai.ChatCompletion.create

    def create_wrapper(**kwargs):
        print("\n=== RAW INPUT TO LLM ===")
        for message in kwargs.get("messages", []):
            print(f"Role: {message['role']}")
            print(f"Content:\n{message['content']}")
            print("-" * 50)
        response = original_create(**kwargs)
        print("\n=== RAW OUTPUT FROM LLM ===")
        print(response.choices[0].message.content)
        print("=" * 25)
        return response

    openai.ChatCompletion.create = create_wrapper

    try:
        # Generate ASC code using the description loaded from file
        asc_code = circuit_generator.generate_asc_code(description, prompt_id)
        print("\n=== FINAL ASC CODE GENERATED FROM DESCRIPTION ===")
        print(asc_code)
    finally:
        # Restore the original OpenAI API call
        openai.ChatCompletion.create = original_create

if __name__ == "__main__":
    test_asc_generation_from_description()

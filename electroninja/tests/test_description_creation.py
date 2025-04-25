import os
import sys
import logging
import openai
from dotenv import load_dotenv

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from electroninja.config.settings import Config
from electroninja.llm.providers.openai import OpenAIProvider
from electroninja.backend.create_description import CreateDescription

# Load environment variables and set up logging
load_dotenv()
logging.basicConfig(level=logging.INFO)

def test_description_creation():
    """Test the description creation functionality:
       1. Create a new description (with no previous description) and save it to output/prompt1/description.txt.
       2. Load that description and use it as the previous description to create a modified description,
          saving the result to output/prompt2/description.txt.
    """
    print("\n====== TEST: DESCRIPTION CREATION ======")
    
    # Initialize configuration, provider and description creator
    config = Config()
    provider = OpenAIProvider(config)
    description_creator = CreateDescription(provider)
    
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
        # Scenario 1: Create description for prompt1 with the new request only (no previous description)
        prev_desc = "None"  # Explicitly pass "None" when there is no previous description
        new_req = "Create a circuit with a 5V battery and a resistor of 10 ohms in series."
        print("\n--- Scenario 1: Creating new description for prompt1 ---")
        description1 = description_creator.create_description(prev_desc, new_req)
        print("\nGenerated Description for prompt1:")
        print(description1)
        
        prompt_id1 = 1
        saved_path1 = description_creator.save_description(description1, prompt_id1)
        print("\nSaved description to:", saved_path1)
        
        # Load the description from prompt1 directory
        loaded_description1 = description_creator.load_description(prompt_id1)
        print("\nLoaded Description for prompt1:")
        print(loaded_description1)
        
        # Scenario 2: Modify the description for prompt2 using the loaded description from prompt1
        new_req2 = "Add a capacitor of 100uF in parallel with the resistor."
        print("\n--- Scenario 2: Creating modified description for prompt2 ---")
        description2 = description_creator.create_description(loaded_description1, new_req2)
        print("\nGenerated Modified Description for prompt2:")
        print(description2)
        
        prompt_id2 = 2
        saved_path2 = description_creator.save_description(description2, prompt_id2)
        print("\nSaved modified description to:", saved_path2)
        
        loaded_description2 = description_creator.load_description(prompt_id2)
        print("\nLoaded Modified Description for prompt2:")
        print(loaded_description2)
        
    finally:
        openai.ChatCompletion.create = original_create

    return description2

if __name__ == "__main__":
    test_description_creation()

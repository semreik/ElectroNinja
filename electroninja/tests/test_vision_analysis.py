import os
import sys
import logging
import openai
from dotenv import load_dotenv

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from electroninja.config.settings import Config
from electroninja.backend.vision_processor import VisionProcessor

load_dotenv()
logging.basicConfig(level=logging.INFO)

def test_vision_analysis(prompt_id, iteration):
    """Test vision analysis of circuit images using prompt_id and iteration for description loading."""
    # Build the image path based on prompt_id and iteration (for informational display)
    image_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "data", "output", f"prompt{prompt_id}", f"output{iteration}", "image.png"
    )
    
    print("\n====== TEST: VISION ANALYSIS ======")
    print(f"Image path: {image_path}")
    print(f"Prompt ID: {prompt_id}, Iteration: {iteration}")
    
    # Load and print the full circuit description
    description_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "data", "output", f"prompt{prompt_id}", "description.txt"
    )
    if os.path.exists(description_path):
        with open(description_path, "r", encoding="utf-8") as f:
            circuit_description = f.read().strip()
        print("\n=== FULL CIRCUIT DESCRIPTION ===")
        print(circuit_description)
        print("=" * 80)
    else:
        print(f"Error: Circuit description file not found at {description_path}")
        return
    
    if not os.path.exists(image_path):
        print(f"Error: Image not found at {image_path}")
        return
    
    config = Config()
    vision_processor = VisionProcessor(config)
    
    original_create = openai.ChatCompletion.create

    def create_wrapper(**kwargs):
        print("\n=== RAW INPUT TO VISION MODEL ===")
        for message in kwargs["messages"]:
            print(f"Role: {message['role']}")
            if isinstance(message['content'], list):
                print("Content: [Contains image data and text]")
                for item in message['content']:
                    if isinstance(item, dict) and item.get('type') == 'text':
                        print(f"Text: {item['text']}")
            else:
                print(f"Content:\n{message['content']}")
            print("-" * 50)
        response = original_create(**kwargs)
        print("\n=== RAW OUTPUT FROM VISION MODEL ===")
        print(response.choices[0].message.content)
        print("=" * 25)
        return response

    try:
        openai.ChatCompletion.create = create_wrapper
    except Exception as e:
        print("Warning: Could not intercept OpenAI API calls")
    
    try:
        # Call the vision processor with prompt_id and iteration; it builds the image path internally.
        analysis = vision_processor.analyze_circuit_image(prompt_id, iteration)
        print("\n=== VISION ANALYSIS RESULT ===")
        print(analysis)
        is_verified = vision_processor.is_circuit_verified(analysis)
        print(f"\nCircuit verified: {'Yes' if is_verified else 'No'}")
    finally:
        try:
            openai.ChatCompletion.create = original_create
        except:
            pass
    
    return analysis

if __name__ == "__main__":
    # Set default variables for prompt_id and iteration
    default_prompt_id = 1
    iteration = 0  # Change this variable to test different iterations
    # Run the test using the default prompt_id and iteration.
    test_vision_analysis(default_prompt_id, iteration)
    print("\n" + "-" * 60 + "\n")

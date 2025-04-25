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

def test_vision_description(prompt_id):
    """Test vision description of circuit images using prompt_id and iteration for description loading."""
    # Build the image path based on prompt_id and iteration (for informational display)
    image_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "data", "output", f"prompt{prompt_id}", f"output0", "image.png"
    )
    
    print("\n====== TEST: IMAGE DESCRIPTION ======")
    print(f"Image path: {image_path}")
    print(f"Prompt ID: {prompt_id}")
    
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
        description = vision_processor.create_description_from_compile(prompt_id)
        print("\n=== VISION DESCRIPTION RESULT ===")
        print(description)
    finally:
        try:
            openai.ChatCompletion.create = original_create
        except:
            pass
    
    return description

if __name__ == "__main__":
    # Set default variables for prompt_id and iteration
    default_prompt_id = 1
    # Run the test using the default prompt_id and iteration.
    test_vision_description(default_prompt_id)
    print("\n" + "-" * 60 + "\n")

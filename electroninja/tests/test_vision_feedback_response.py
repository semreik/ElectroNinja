import os
import sys
import logging
import openai
from dotenv import load_dotenv

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from electroninja.config.settings import Config
from electroninja.llm.providers.openai import OpenAIProvider
from electroninja.backend.chat_response_generator import ChatResponseGenerator

load_dotenv()
logging.basicConfig(level=logging.INFO)

def test_vision_feedback_response(vision_feedback):
    """Test generating user-friendly feedback response with printed LLM I/O"""
    print("\n====== TEST: VISION FEEDBACK RESPONSE ======")
    print("Vision feedback:")
    print(vision_feedback)
    
    config = Config()
    llm_provider = OpenAIProvider(config)
    chat_generator = ChatResponseGenerator(llm_provider)
    
    original_create = openai.ChatCompletion.create

    def create_wrapper(**kwargs):
        print("\n=== RAW INPUT TO LLM ===")
        for message in kwargs["messages"]:
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
        response = chat_generator.generate_feedback_response(vision_feedback)
        print("\n=== FEEDBACK RESPONSE ===")
        print(response)
        is_success = vision_feedback.strip() == 'Y'
        print(f"\nCircuit success: {'Yes' if is_success else 'No'}")
    finally:
        openai.ChatCompletion.create = original_create
    
    return response

if __name__ == "__main__":
    print("\n=== TESTING SUCCESSFUL CIRCUIT ===")
    test_vision_feedback_response("Y")
    
    print("\n=== TESTING CIRCUIT WITH ISSUES ===")
    failure_feedback = """1. **Components Present**:
   - Voltage source (V1 = 50V)
   - Resistor R1 = 200 ohms
   - Resistor R2 = 100 ohms

2. **Connections**:
   - Resistors R1 and R2 are in parallel.
   - The parallel combination is connected across the voltage source.

3. **Issues**:
   - The current configuration has R1 and R2 in parallel, not in series.

4. **Recommendations for Fixing**:
   - Connect R1 and R2 in series.
   - Connect one terminal of R1 to the positive end of V1.
   - Connect the other terminal of R2 to the negative end (or ground) of V1.
   - Take the output voltage across R2 (or R1, depending on the desired division ratio).
"""
    test_vision_feedback_response(failure_feedback)

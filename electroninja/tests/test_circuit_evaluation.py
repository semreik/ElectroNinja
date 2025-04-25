import os
import sys
import logging
import openai
from dotenv import load_dotenv

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from electroninja.config.settings import Config
from electroninja.llm.providers.openai import OpenAIProvider
from electroninja.backend.request_evaluator import RequestEvaluator

load_dotenv()
logging.basicConfig(level=logging.INFO)

def test_circuit_evaluation(prompt, prompt_id=5):
    """Test circuit relevance evaluation, saving components.txt, and loading it back."""
    print("\n====== TEST: CIRCUIT RELEVANCE EVALUATION ======")
    print(f"Evaluating prompt: '{prompt}' with prompt ID: {prompt_id}")
    
    config = Config()
    llm_provider = OpenAIProvider(config)
    request_evaluator = RequestEvaluator(llm_provider)
    
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
        # Use the new evaluate_request() which saves components.txt if result != 'N'
        evaluation_result = request_evaluator.evaluate_request(prompt, prompt_id)
        print("\n=== EVALUATION RESULT ===")
        if evaluation_result.strip().upper() == 'N':
            print("Circuit-related: No")
        else:
            print(f"Circuit-related components: {evaluation_result}")
        
        # Load and print the saved components.txt file content
        saved_components = request_evaluator.load_components(prompt_id)
        print("\n=== LOADED COMPONENTS FILE ===")
        print(f"Saved components: {saved_components}")
    finally:
        openai.ChatCompletion.create = original_create

    return evaluation_result

if __name__ == "__main__":
    prompts = [
        "Create a circuit with two resistors in parallel",
        "Design a simple RC low-pass filter",
        "Tell me about World War 2",
    ]
    for prompt in prompts:
        print(f"\n*** TESTING PROMPT: '{prompt}' ***")
        test_circuit_evaluation(prompt, prompt_id=1)

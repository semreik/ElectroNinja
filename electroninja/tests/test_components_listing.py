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

def test_components_listing(prompt_id=1):
    """Test circuit relevance evaluation, saving components.txt, and loading it back."""
  
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
        components = request_evaluator.list_components(prompt_id)
        print("\n=== EVALUATION RESULT ===")
        print(components)
    finally:
        openai.ChatCompletion.create = original_create

    return components

if __name__ == "__main__":

    test_components_listing(prompt_id=1)

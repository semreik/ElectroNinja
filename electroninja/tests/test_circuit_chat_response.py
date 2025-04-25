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

def test_circuit_chat_response(prompt):
    """Test generating chat responses and print LLM I/O"""
    print("\n====== TEST: CIRCUIT CHAT RESPONSE ======")
    print(f"Prompt: '{prompt}'")
    
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
        chat_response = chat_generator.generate_response(prompt)
        print("\n=== FINAL CHAT RESPONSE ===")
        print(chat_response)
    finally:
        openai.ChatCompletion.create = original_create

    return chat_response

if __name__ == "__main__":
    print("\n=== TESTING CIRCUIT-RELATED PROMPT ===")
    test_circuit_chat_response("Create a circuit with two resistors in parallel")
    
    print("\n=== TESTING NON-CIRCUIT-RELATED PROMPT ===")
    test_circuit_chat_response("Tell me about World War 2")

import logging
from electroninja.llm.providers.openai import OpenAIProvider

logger = logging.getLogger('electroninja')

class ChatResponseGenerator:
    """
    Generates chat responses for the user using the OpenAI provider.
    """
    def __init__(self, openai_provider: OpenAIProvider):
        self.provider = openai_provider
        self.logger = logger

    def generate_response(self, prompt: str) -> str:
        self.logger.info(f"Generating chat response for prompt: '{prompt}'")
        # Delegates to the provider's method
        response = self.provider.generate_chat_response(prompt)
        self.logger.info(f"Chat response generated: {response}")
        return response

    def generate_feedback_response(self, vision_feedback: str) -> str:
        self.logger.info("Generating vision feedback response")
        # Delegates to the provider's method
        response = self.provider.generate_vision_feedback_response(vision_feedback)
        self.logger.info(f"Feedback response generated: {response}")
        return response

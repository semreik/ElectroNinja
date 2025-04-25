from abc import ABC, abstractmethod

class LLMProvider(ABC):
    """Base class for LLM providers"""

    @abstractmethod
    def generate_asc_code(self, prompt: str, examples=None) -> str:
        """
        Generate ASC code based on a prompt and optional examples.

        Args:
            prompt (str): The user's prompt.
            examples (list, optional): Examples for retrieval-augmented generation (RAG).

        Returns:
            str: The generated ASC code.
        """
        pass

    @abstractmethod
    def generate_chat_response(self, prompt: str) -> str:
        """
        Generate a chat response for the given prompt.

        Args:
            prompt (str): The user's prompt.

        Returns:
            str: The generated chat response.
        """
        pass

    @abstractmethod
    def refine_asc_code(self, request: str, history: list) -> str:
        """
        Refine ASC code based on the original request and conversation history.

        Args:
            request (str): The original user's request.
            history (list): The conversation history.

        Returns:
            str: The refined ASC code.
        """
        pass

    @abstractmethod
    def generate_vision_feedback_response(self, vision_feedback: str) -> str:
        """
        Generate a user-friendly feedback response based on vision feedback.

        Args:
            vision_feedback (str): The raw vision feedback.

        Returns:
            str: The generated feedback response.
        """
        pass

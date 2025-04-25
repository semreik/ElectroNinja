# electroninja/config/settings.py
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Centralized configuration for ElectroNinja"""
    
    # Application paths
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    OUTPUT_DIR = os.path.join(BASE_DIR, "data", "output")
    EXAMPLES_DIR = os.path.join(BASE_DIR, "data", "examples_asc")
    
    # LTSpice configuration
    LTSPICE_PATH = os.getenv("LTSPICE_PATH", 
                             r"C:\Users\leegj\AppData\Local\Programs\ADI\LTspice\LTspice.exe")
    
    # LLM configuration
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    ASC_MODEL = os.getenv("ASC_MODEL", "o3-mini")
    CHAT_MODEL = os.getenv("CHAT_MODEL", "gpt-4o-mini")
    EVALUATION_MODEL = os.getenv("EVALUATION_MODEL", "gpt-4o-mini")
    DESCRIPTION_MODEL = os.getenv("DESCRIPTION_MODEL", "gpt-4o-mini")
    MERGER_MODEL = os.getenv("MERGER_MODEL", "gpt-4o-mini")
    COMPONENT_MODEL = os.getenv("COMPONENT_MODEL", "gpt-4o-mini")
    
    # Vision configuration
    OPENAI_VISION_MODEL = os.getenv("OPENAI_VISION_MODEL", "gpt-4o")

    # Vector DB configuration
    VECTOR_DB_DIR = os.path.join(BASE_DIR, "data", "vector_db")
    VECTOR_DB_INDEX = os.path.join(VECTOR_DB_DIR, "faiss_index.bin")
    VECTOR_DB_METADATA = os.path.join(VECTOR_DB_DIR, "metadata_list.pkl")
    
    # Create necessary directories
    @classmethod
    def ensure_directories(cls):
        """Ensure all required directories exist"""
        os.makedirs(cls.OUTPUT_DIR, exist_ok=True)
        os.makedirs(cls.VECTOR_DB_DIR, exist_ok=True)
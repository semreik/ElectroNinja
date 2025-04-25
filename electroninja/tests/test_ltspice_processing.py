import os
import sys
import logging
import platform
import time
from dotenv import load_dotenv

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from electroninja.config.settings import Config
from electroninja.backend.ltspice_manager import LTSpiceManager

load_dotenv()
logging.basicConfig(level=logging.INFO)

def test_ltspice_processing(asc_code, prompt_id=1, iteration=0):
    """Test LTSpice processing workflow; prints ASC code and output file paths"""
    print("\n====== TEST: LTSPICE PROCESSING ======")
    print(f"Platform: {platform.system()} {platform.release()}")
    print("\n=== ASC CODE ===")
    print(asc_code)
    print(f"\n=== PROCESSING CIRCUIT ===")
    print(f"Prompt ID: {prompt_id}, Iteration: {iteration}")
    print(f"Starting at: {time.strftime('%H:%M:%S')}")
    
    config = Config()
    ltspice_manager = LTSpiceManager(config)
    result = ltspice_manager.process_circuit(asc_code, prompt_id, iteration)
    print(f"Finished at: {time.strftime('%H:%M:%S')}")
    
    if not result:
        print("Processing failed!")
        return None
    
    asc_path, image_path = result
    print("\n=== RESULTS ===")
    print(f"ASC file: {asc_path}")
    print(f"Image file: {image_path}")
    print("\n=== VERIFICATION ===")
    print(f"ASC file exists: {'Yes' if os.path.exists(asc_path) else 'No'}")
    print(f"Image file exists: {'Yes' if os.path.exists(image_path) else 'No'}")
    
    return result

if __name__ == "__main__":
    test_asc_code = """Version 4
SHEET 1 880 680
WIRE 224 80 80 80
WIRE 336 80 224 80
WIRE 80 128 80 80
WIRE 224 128 224 80
WIRE 336 128 336 80
WIRE 80 240 80 208
WIRE 224 240 224 208
WIRE 224 240 80 240
WIRE 336 240 336 208
WIRE 336 240 224 240
SYMBOL voltage 80 112 R0
SYMATTR InstName V1
SYMATTR Value 50
SYMBOL res 208 112 R0
SYMATTR InstName R1
SYMATTR Value 200
SYMBOL res 320 112 R0
SYMATTR InstName R2
SYMATTR Value 100
TEXT 136 264 Left 2 !.op
"""
    test_ltspice_processing(test_asc_code)

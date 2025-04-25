import logging
import os
from typing import Tuple, Optional
from electroninja.config.settings import Config
from electroninja.ltspice import LTSpiceInterface

logger = logging.getLogger('electroninja')

class LTSpiceManager:
    """
    Manages the processing of ASC code with LTSpice.
    """
    def __init__(self, config: Config = None):
        self.config = config or Config()
        self.ltspice_interface = LTSpiceInterface(self.config)
        self.logger = logger

    def process_circuit(self, asc_code: str, prompt_id: int, iteration: int) -> Optional[Tuple[str, str]]:
        try:
            # Print input information
            print(f"\n{'='*80}\nLTSPICE MANAGER INPUT:\n{'='*80}")
            print(f"Prompt ID: {prompt_id}, Iteration: {iteration}")
            print(f"ASC code (first 100 chars):\n{asc_code[:100]}...")
            print('='*80)
            
            asc_path, image_path = self.get_output_paths(prompt_id, iteration)
            output_dir = os.path.dirname(asc_path)
            if not os.path.exists(output_dir):
                os.makedirs(output_dir, exist_ok=True)
                self.logger.info(f"Created output structure: {output_dir}")
                
            with open(asc_path, 'w') as f:
                f.write(asc_code)
            self.logger.info(f"Wrote ASC file: {asc_path}")
            
            self.logger.info(f"Processing circuit with LTSpice (Prompt {prompt_id}, Iteration {iteration})")
            result = self.ltspice_interface.process_circuit(asc_code, prompt_id=prompt_id, iteration=iteration)
            
            # Print the result
            print(f"\n{'='*80}\nLTSPICE MANAGER OUTPUT:\n{'='*80}")
            if not result:
                print("LTSpice processing failed")
                self.logger.error("LTSpice processing failed")
                print('='*80)
                return None
                
            asc_path, image_path = result
            print(f"LTSpice processing successful")
            print(f"ASC path: {asc_path}")
            print(f"Image path: {image_path}")
            print(f"Output directory: {output_dir}")
            print('='*80)
            
            self.logger.info(f"LTSpice processing successful. ASC: {asc_path}, Image: {image_path}")
            return asc_path, image_path
        except Exception as e:
            self.logger.error(f"Unexpected error in LTSpice processing: {str(e)}")
            
            # Print the error
            print(f"\n{'='*80}\nLTSPICE MANAGER ERROR:\n{'='*80}")
            print(f"Error: {str(e)}")
            print('='*80)
            
            return None

    def get_output_paths(self, prompt_id: int, iteration: int) -> Tuple[str, str]:
        output_dir = os.path.join(
            self.config.OUTPUT_DIR, 
            f"prompt{prompt_id}", 
            f"output{iteration}"
        )
        if not os.path.exists(output_dir):
            os.makedirs(output_dir, exist_ok=True)
        asc_path = os.path.join(output_dir, "code.asc")
        image_path = os.path.join(output_dir, "image.png")
        return asc_path, image_path
import os
import openai
import logging
from electroninja.config.settings import Config
from electroninja.llm.providers.base import LLMProvider
from electroninja.llm.prompts.circuit_prompts import (
    ASC_SYSTEM_PROMPT,
    ASC_REFINEMENT_PROMPT_TEMPLATE,
    CIRCUIT_RELEVANCE_EVALUATION_PROMPT,
    DESCRIPTION_PROMPT
)
from electroninja.llm.prompts.chat_prompts import (
    CIRCUIT_CHAT_PROMPT,
    VISION_FEEDBACK_PROMPT
)

from electroninja.llm.prompts.button_prompts import (
    COMPILE_CODE_COMP_PROMPT
)

logger = logging.getLogger('electroninja')

class OpenAIProvider(LLMProvider):
    """OpenAI implementation of LLM provider containing all LLM functionalities."""
    
    def __init__(self, config=None):
        self.config = config or Config()
        openai.api_key = self.config.OPENAI_API_KEY or os.getenv("OPENAI_API_KEY")
        self.asc_gen_model = self.config.ASC_MODEL
        self.chat_model = self.config.CHAT_MODEL
        self.evaluation_model = self.config.EVALUATION_MODEL  
        self.merger_model = self.config.MERGER_MODEL
        self.description_model = self.config.DESCRIPTION_MODEL
        self.logger = logger        
        
    def evaluate_circuit_request(self, prompt: str) -> str:
        try:
            # Format the evaluation prompt with the new instructions
            evaluation_prompt = CIRCUIT_RELEVANCE_EVALUATION_PROMPT.format(prompt=prompt)
            logger.info(f"Evaluating if request is circuit-related: {prompt}")
            response = openai.ChatCompletion.create(
                model=self.evaluation_model,
                messages=[{"role": "user", "content": evaluation_prompt}]
            )
            # Return the raw result string: either 'N' or the component letters (e.g., "V, R, C")
            result = response.choices[0].message.content.strip()
            logger.info(f"Evaluation result for '{prompt}': {result}")
            return result
        except Exception as e:
            logger.error(f"Error evaluating request: {str(e)}")
            # In case of error, return "N" as a safe fallback.
            return "N"

        
    def create_description(self, previous_description: str, new_request: str) -> str:
        """
        Merge a current circuit description with a new modification request to a new description.
        
        Args:
            previous_description: The previous circuit description
            new_request: The new modification request from the user
            
        Returns:
            A merged, comprehensive circuit description
        """
        previous_description = previous_description if previous_description is not None else "None"

        description_prompt = DESCRIPTION_PROMPT.format(
            previous_description=previous_description,
            new_request=new_request
        )
        self.logger.info("Generating description using prompt:\n" + description_prompt)
        
        try:
            response = openai.ChatCompletion.create(
                model=self.description_model,
                messages=[{"role": "user", "content": description_prompt}]
            )
            new_description = response.choices[0].message.content.strip()
            
            self.logger.info("Merged result:\n" + new_description)
            
            return new_description
        except Exception as e:
            self.logger.error("Error generating description: " + str(e))
            return new_request
    
    def extract_clean_asc_code(self, asc_code: str) -> str:
        if "Version 4" in asc_code:
            idx = asc_code.find("Version 4")
            return asc_code[idx:].strip()
        return asc_code.strip()
    
    def _load_instruction(self, filename: str) -> str:
        """
        Loads an instruction file from electroninja/llm/prompts/instructions/ directory.
        """
        instruct_path = os.path.join("electroninja", "llm", "prompts", "instructions", filename)
        try:
            with open(instruct_path, "r", encoding="utf-8") as f:
                return f.read()
        except Exception as e:
            self.logger.error(f"Error loading {filename}: {str(e)}")
            return ""

    def _build_prompt(self, description: str, examples=None, prompt_id: int = None) -> str:
        """
        Builds the complete prompt for ASC generation.
        
        It includes:
         1. General instructions and battery instructions.
         2. Additional component instructions based on the components file.
         3. Top examples from the vector DB.
         4. The final circuit description.
         5. A final task instruction.
        """
        prompt_parts = []

        # 1. General instructions.
        general_instruct = self._load_instruction("general_instruct.txt")
        prompt_parts.append("=== GENERAL INSTRUCTIONS ===\n" + general_instruct + "\n")

        # 2. Battery instructions.
        battery_instruct = self._load_instruction("battery_instruct.txt")
        prompt_parts.append("=== BATTERY INSTRUCTIONS ===\n" + battery_instruct + "\n")

        # 3. Additional component instructions based on saved components.
        if prompt_id is not None:
            components_path = os.path.join("data", "output", f"prompt{prompt_id}", "components.txt")
            if os.path.exists(components_path):
                try:
                    with open(components_path, "r", encoding="utf-8") as f:
                        components_text = f.read().strip().upper()
                    # For each component letter, add corresponding instructions.
                    if "R" in components_text:
                        resistor_instruct = self._load_instruction("resistor_instruct.txt")
                        prompt_parts.append("=== RESISTOR INSTRUCTIONS ===\n" + resistor_instruct + "\n")
                    if "C" in components_text:
                        capacitor_instruct = self._load_instruction("capacitor_instruct.txt")
                        prompt_parts.append("=== CAPACITOR INSTRUCTIONS ===\n" + capacitor_instruct + "\n")
                    if "L" in components_text:
                        inductor_instruct = self._load_instruction("inductor_instruct.txt")
                        prompt_parts.append("=== INDUCTOR INSTRUCTIONS ===\n" + inductor_instruct + "\n")
                    if "D" in components_text:
                        diode_instruct = self._load_instruction("diode_instruct.txt")
                        prompt_parts.append("=== DIODE INSTRUCTIONS ===\n" + diode_instruct + "\n")
                except Exception as e:
                    self.logger.error(f"Error reading components file: {str(e)}")

        # 4. Include examples from the vector database, if any.
        # if examples and len(examples) > 0:
        #     prompt_parts.append(
        #         "You also will be provided with three example ASC files that are relevant to the user's query. " 
        #         "However, only use these as a reference to understand the syntax for necessary components and their connections, DO NOT try to copy their coordinate system. "
        #         "Also, carefully examine how multiple wires are used in the example circuits to create corners when connecting two nodes to increase spacing, instead of connecting a node with a single straight wire and making the whole circuit tight. "
        #         "Come up with your own coordinates and connections using the instructions above, keeping in mind the location of the reference node and the offset translations.\n"
        #         "Below are three examples of circuits similar to the user's request:\n\n"
        #     )
        #     prompt_parts.append("=== EXAMPLES FROM SIMILAR CIRCUITS ===\n")
        #     for i, example in enumerate(examples, start=1):
        #         ex_desc = example.get("metadata", {}).get("description", "No description provided")
        #         ex_asc = example.get("asc_code", "")
        #         prompt_parts.append(f"Example {i}:\nDescription: {ex_desc}\nASC Code:\n{ex_asc}\n")
        #     prompt_parts.append("\n")

        # 5. Append the circuit description.
        prompt_parts.append("=== CIRCUIT DESCRIPTION ===\n" + description + "\n")

        # 6. Final task instruction.
        prompt_parts.append("=== TASK ===\nBased on the above instructions, examples, and circuit description, generate the complete .asc code. Your output must contain only valid .asc code with no extra commentary.")

        final_prompt = "\n".join(prompt_parts)
        return final_prompt

    def generate_asc_code(self, description: str, examples=None, prompt_id: int = None) -> str:
        """
        Generates the ASC code for the given circuit description by building a composite prompt
        that includes system instructions, various component instructions, examples, and the description.
        """
        self.logger.info(f"Generating ASC code for circuit description: {description}")
        system_prompt = ASC_SYSTEM_PROMPT  # This will be sent as the system message

        user_prompt = self._build_prompt(description, examples, prompt_id)

        print(f"\n{'='*80}\nASC GENERATION PROMPT:\n{'='*80}")
        print(user_prompt)

        try:
            response = openai.ChatCompletion.create(
                model=self.asc_gen_model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
            )
            asc_code = response.choices[0].message.content.strip()
            if asc_code.upper() == "N":
                return "N"
            else:
                return self.extract_clean_asc_code(asc_code)
        except Exception as e:
            self.logger.error(f"Error generating ASC code: {str(e)}")
            return "Error: Failed to generate circuit"


    
    def generate_chat_response(self, prompt: str) -> str:
        try:
            chat_prompt = f"{CIRCUIT_CHAT_PROMPT.format(prompt=prompt)}"
            logger.info(f"Generating chat response for prompt: {prompt}")
            response = openai.ChatCompletion.create(
                model=self.chat_model,
                messages=[{"role": "user", "content": chat_prompt}]
            )
            chat_response = response.choices[0].message.content.strip()
            return chat_response
        except Exception as e:
            logger.error(f"Error generating chat response: {str(e)}")
            return "Error generating chat response"
    
    def generate_vision_feedback_response(self, vision_feedback: str) -> str:
        try:
            is_success = vision_feedback.strip() == 'Y'
            prompt = VISION_FEEDBACK_PROMPT.format(
                vision_feedback=vision_feedback
            )
            logger.info(f"Generating vision feedback response (success={is_success})")
            response = openai.ChatCompletion.create(
                model=self.chat_model,
                messages=[{"role": "user", "content": prompt}]
            )
            feedback_response = response.choices[0].message.content.strip()
            return feedback_response
        except Exception as e:
            logger.error(f"Error generating vision feedback response: {str(e)}")
            return "Error generating vision feedback response"
    
    def _build_refinement_prompt(self, prompt_id: int, iteration: int, vision_feedback: str) -> str:
        """
        Builds the composite prompt for refining ASC code using the new template.
        It loads:
         - The original circuit description from data/output/prompt{prompt_id}/description.txt
         - The incorrect ASC code from data/output/prompt{prompt_id}/output{iteration}/code.asc
         - The provided vision feedback
         - The instruction files (general, battery, and additional component instructions)
        Then substitutes these into the ASC_REFINEMENT_PROMPT_TEMPLATE.
        """
        # Load original circuit description
        description_path = os.path.join("data", "output", f"prompt{prompt_id}", "description.txt")
        if os.path.exists(description_path):
            with open(description_path, "r", encoding="utf-8") as f:
                original_description = f.read().strip()
        else:
            original_description = "Description not found."
        
        # Load incorrect ASC code
        asc_path = os.path.join("data", "output", f"prompt{prompt_id}", f"output{iteration}", "code.asc")
        if os.path.exists(asc_path):
            with open(asc_path, "r", encoding="utf-8") as f:
                incorrect_asc = f.read().strip()
        else:
            incorrect_asc = "Incorrect ASC code not found."
        
        # Use the provided vision feedback (if empty, default text)
        if not vision_feedback:
            vision_feedback = "No vision feedback provided."
        
        # Load instruction files
        general_instruct = self._load_instruction("general_instruct.txt")
        battery_instruct = self._load_instruction("battery_instruct.txt")
        instructions_parts = []
        instructions_parts.append("GENERAL INSTRUCTIONS:\n" + general_instruct)
        instructions_parts.append("BATTERY INSTRUCTIONS:\n" + battery_instruct)
        
        # Additional instructions based on components file
        components_path = os.path.join("data", "output", f"prompt{prompt_id}", "components.txt")
        if os.path.exists(components_path):
            try:
                with open(components_path, "r", encoding="utf-8") as f:
                    comp_text = f.read().strip().upper()
                if "R" in comp_text:
                    resistor_instruct = self._load_instruction("resistor_instruct.txt")
                    instructions_parts.append("RESISTOR INSTRUCTIONS:\n" + resistor_instruct)
                if "C" in comp_text:
                    capacitor_instruct = self._load_instruction("capacitor_instruct.txt")
                    instructions_parts.append("CAPACITOR INSTRUCTIONS:\n" + capacitor_instruct)
                if "L" in comp_text:
                    inductor_instruct = self._load_instruction("inductor_instruct.txt")
                    instructions_parts.append("INDUCTOR INSTRUCTIONS:\n" + inductor_instruct)
                if "D" in comp_text:
                    diode_instruct = self._load_instruction("diode_instruct.txt")
                    instructions_parts.append("DIODE INSTRUCTIONS:\n" + diode_instruct)
            except Exception as e:
                self.logger.error(f"Error reading components file: {str(e)}")
        instructions_combined = "\n\n".join(instructions_parts)
        
        # Build the final prompt using the new template from circuit_prompts.py
        refinement_prompt = ASC_REFINEMENT_PROMPT_TEMPLATE.format(
            original_description=original_description,
            incorrect_asc=incorrect_asc,
            vision_feedback=vision_feedback,
            instruction_files=instructions_combined
        )
        return refinement_prompt

    def refine_asc_code(self, prompt_id: int, iteration: int, vision_feedback: str) -> str:
        """
        Refines the incorrect ASC code using the composite refinement prompt.
        
        Args:
            prompt_id (int): Identifier for the current prompt session.
            iteration (int): The iteration number corresponding to the incorrect code.
            vision_feedback (str): The feedback from the vision model.
        
        Returns:
            str: The refined, corrected ASC code.
        """
        try:
            refinement_prompt = self._build_refinement_prompt(prompt_id, iteration, vision_feedback)
            self.logger.info("Refining ASC code based on feedback using new refinement prompt.")
            response = openai.ChatCompletion.create(
                model=self.asc_gen_model,
                messages=[
                    {"role": "system", "content": ASC_SYSTEM_PROMPT},
                    {"role": "user", "content": refinement_prompt}
                ]
            )
            refined_asc = response.choices[0].message.content.strip()
            return refined_asc
        except Exception as e:
            self.logger.error(f"Error refining ASC code: {str(e)}")
            return "Error refining ASC code"
        
    def list_components(self, asc_code: str) -> str:
        """
        Lists the components present in the given ASC code.
        
        Args:
            asc_code (str): The ASC code to analyze.
        
        Returns:
            str: A string listing the components found in the ASC code.
        """
        try:
            prompt = COMPILE_CODE_COMP_PROMPT.format(asc_code=asc_code)
            self.logger.info("Listing components from ASC code.")
            response = openai.ChatCompletion.create(
                model=self.merger_model,
                messages=[{"role": "user", "content": prompt}]
            )
            components = response.choices[0].message.content.strip()
            return components
        except Exception as e:
            self.logger.error(f"Error listing components: {str(e)}")
            return "Error listing components"
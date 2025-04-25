# ElectroNinja: A cursor for electrical engineers

ElectroNinja is an advanced AI-powered application that functions as an electrical engineer. It interprets user requests, generates circuit descriptions, creates LTSpice ASC code, and iteratively refines circuit designs using a combination of GPT-based language models, a vision analysis module, and LTSpice simulation.

## Overview

ElectroNinja processes a user's circuit request through several coordinated steps:

1. **User Request Evaluation**  
   The application first evaluates whether a user's request is related to electrical circuits. If it is, the system extracts and saves component identifiers (e.g., R for resistor, C for capacitor) in a dedicated output file. Otherwise, it generates a polite, non-circuit-related response.

2. **Circuit Description Generation**  
   For valid circuit requests, the system uses an LLM to generate a detailed circuit description. For modification requests, it merges the new request with the previous description to create an updated version.

3. **ASC Code Generation**  
   The application builds a comprehensive prompt by combining:
   - General and battery-specific instructions
   - Component-specific instructions (resistor, capacitor, inductor, diode) based on the evaluation results
   - Example circuits retrieved from a vector database  
   This prompt is sent to the circuit generation model which produces an LTSpice-compatible ASC code file.

4. **LTSpice Processing**  
   The generated ASC code is passed to LTSpice via an automated interface. LTSpice processes the code to produce a circuit diagram (saved as a PDF), which is then converted to a PNG image and displayed in the application's middle panel.

5. **Vision Feedback and Iterative Refinement**  
   A vision model analyzes the generated circuit image against the saved description. If the circuit is verified as correct (feedback equals 'Y'), the process is finalized. Otherwise, the system provides detailed feedback and enters an iterative refinement loop, updating the ASC code and re-running the simulation until the circuit meets the requirements or a maximum number of iterations is reached.

6. **User Interface**  
   The application features a rich GUI built with PyQt5, which includes:
   - A **left panel** for ASC code editing and compile actions.
   - A **middle panel** for displaying the circuit diagram.
   - A **right panel** with a chat interface to interact with the AI assistant.
   - A **top bar** displaying the application title and version.

## File Structure Overview

- **data/**  
  Contains example ASC files, vector database files, and output directories where circuit designs and iterations are stored.

- **electroninja/backend/**  
  Implements core functionalities:
  - Request evaluation (`request_evaluator.py`)
  - Chat response generation (`chat_response_generator.py`)
  - Circuit generation and refinement (`circuit_generator.py`)
  - LTSpice integration (`ltspice_manager.py`)
  - Vision feedback processing (`vision_processor.py`)
  - Description creation (`create_description.py`)

- **electroninja/llm/**  
  Contains providers for OpenAI models, prompt templates (for circuit design, chat, vision analysis), and vector store functionalities.

- **electroninja/ui/**  
  Provides the GUI components and panels (left, middle, right, top bar) and the main window (`main_window.py`).

- **tests/**  
  Includes unit tests for ASC generation, refinement, circuit evaluation, chat response, and component listing.

- **config/**  
  Contains settings (`settings.py`) and logging configuration (`logging_config.py`).

## Getting Started

To run ElectroNinja, follow these steps:

1. **Download LTSpice**  
   Download and install LTSpice from:  
   [https://www.analog.com/en/resources/design-tools-and-calculators/ltspice-simulator.html](https://www.analog.com/en/resources/design-tools-and-calculators/ltspice-simulator.html)

2. **Configure LTSpice Path**  
   In the `electroninja/config/settings.py` file, update the `LTSPICE_PATH` variable with the full path to your `LTspice.exe` file. For example:
   ```python
   LTSPICE_PATH = r"C:\Path\To\LTspice\LTspice.exe"
   ```

3. **Set Up OpenAI API Key**  
   Create a `.env` file in the base directory of the project and add your OpenAI API key:
   ```ini
   OPENAI_API_KEY="your_openai_api_key_here"
   ```

4. **Install Dependencies**  
   Install all required dependencies by running:
   ```bash
   pip install -r requirements.txt
   ```

5. **Run the Application**  
   Start the application by running the `main.py` file:
   ```bash
   python main.py
   ```
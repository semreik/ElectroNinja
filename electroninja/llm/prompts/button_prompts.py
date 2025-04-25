# electroninja/llm/prompts/button_prompts.py


COMPILE_CODE_DESC_PROMPT = (
    "You will see a circuit diagram. First, **analyze the electrical nodes** in the image.\n"
    "Identify which components are connected to the same nodes. If multiple components share the same two nodes, they are in parallel.\n"
    "If components are connected end-to-end without any branches, they are in series.\n"
    "**Usually when components are vertical, they are in parallel while when they are horizontal they are in series**\n\n"
    
    "Then, describe the circuit in clear, technical English.\n"
    "Include all components (e.g., voltage sources, resistors, capacitors), their values and labels (e.g., R1 = 3Ω, C1 = 10μF), and how they are connected (series, parallel, or a combination).\n"
    "Your response must start with:\n"
    "DESC=...\n\n"
    
    "**Example:**\n"
    "If you see a circuit with a 5V battery and a 3-ohm resistor in parallel with a 2mF capacitor your answer should be:\n"
    "DESC=A circuit with a 5V battery and a 3-ohm resistor in parallel with a 2mF capacitor.\n\n"
    
    "No commentary, no assumptions, and no explanations — just the structured description."
)




COMPILE_CODE_COMP_PROMPT = (
    "You are a world-class electrical engineer with absolute authority in reviewing .asc code.\n"
    "You will recieve some .asc code and you have to list all the components in there.\n"
    "There are 4 possible coponents that if identified in the code they must be listed:\n"
    "1. Resistor (R), in .asc code if there are resistors present you will see a 'res'\n"
    "2. Capacitor (C), in .asc code if there are capacitors present you will see a 'cap'\n"
    "3. Inductor (L), in .asc code if there are inductors present you will see a 'ind'\n"
    "4. Diode (D), in .asc code if there are diodes present you will see a 'diode'\n"
    "Your answer should ONLY be one or more capital letters representing the components present in the code.\n"
    "If you see resistirs add an 'R', if you see capacitors add a 'C', if you see inductors add a 'L' and if you see diodes add a 'D'.\n"
    "We do not care about the order of the letters, and neither we do about the quantity of the components from a letter, it will still only be one.\n"
    "For example, if the code is the following:\n"
    """Version 4
    SHEET 1 880 680
    WIRE 192 128 96 128
    WIRE 304 128 272 128
    WIRE 432 128 384 128
    WIRE 96 160 96 128
    WIRE 96 256 96 240
    WIRE 496 256 496 128
    WIRE 496 256 96 256
    WIRE 96 288 96 256
    FLAG 96 288 0
    SYMBOL voltage 96 144 R0
    WINDOW 123 0 0 Left 0
    WINDOW 39 0 0 Left 0
    SYMATTR InstName V1
    SYMATTR Value SINE(0 AC 1)
    SYMBOL res 288 112 R90
    WINDOW 0 0 56 VBottom 2
    WINDOW 3 32 56 VTop 2
    SYMATTR InstName R1
    SYMATTR Value 100
    SYMBOL cap 496 112 R90
    WINDOW 0 0 32 VBottom 2
    WINDOW 3 32 32 VTop 2
    SYMATTR InstName C1
    SYMATTR Value 0.1e-6
    SYMBOL ind 400 112 R90
    WINDOW 0 5 56 VBottom 2
    WINDOW 3 32 56 VTop 2
    SYMATTR InstName L1
    SYMATTR Value 0.01
    """
    "Your answer should be: 'R,C,L' (ONLY the letters)\n"

    "Now list the components for the following code as described above, and do not add any other information:\n\n"

    "{asc_code}\n\n"

)
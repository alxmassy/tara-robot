# main.py

import os
from dotenv import load_dotenv

from tara_core.voice_interface import VoiceInterface
from tara_core.assistant_tasks import AssistantTasks
from tara_core.memory_manager import MemoryManager 
# RobotControl and VisionSystem imports are removed as requested

# --- Load environment variables from .env file ---
load_dotenv()

# --- Get Gemini API Key from environment variable ---
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY") 

if not GEMINI_API_KEY:
    print("ERROR: GEMINI_API_KEY not found or is empty. Please set it in your .env file or environment variables.")
    # For a hackathon, you might want to exit here or explicitly fall back to rule-based mode
    # For now, we'll let it proceed and VoiceInterface will handle the 'None' case.
    # exit(1) 


def main():
    print("Starting TARA's core...")
    
    # Initialize core components
    tara_assistant = AssistantTasks()
    tara_memory = MemoryManager() 

    # Create a dictionary to map tool names to their corresponding object methods.
    # This allows Gemini to "call" methods on any of these objects.
    # We exclude internal/private methods (startswith('_')) and 'log_event' for memory.
    tool_executor_map = {
        **{name: getattr(tara_assistant, name) for name in dir(tara_assistant) if callable(getattr(tara_assistant, name)) and not name.startswith('_')},
        # RobotControl and VisionSystem methods are intentionally omitted here as per your request.
        # Ensure MemoryManager methods ARE included:
        **{name: getattr(tara_memory, name) for name in dir(tara_memory) if callable(getattr(tara_memory, name)) and not name.startswith('_') and name != 'log_event'}, 
    }

    # Initialize VoiceInterface, passing all necessary components
    tara_voice = VoiceInterface(
        assistant_tasks=tool_executor_map, 
        memory_manager=tara_memory,       
        gemini_api_key=GEMINI_API_KEY
    ) 

    tara_voice.speak("Hello there! I am TARA, your personal companion robot. How can I assist you today?")

    while True:
        command_text = tara_voice.listen_for_command()
        
        # Log the user's raw command
        tara_memory.log_event("user_command", {"command": command_text}) 
        
        # If the user explicitly asks to quit, handle it here.
        lower_command_text = command_text.lower()
        if ("quit" in lower_command_text or 
            "exit" in lower_command_text or 
            "goodbye" in lower_command_text):
            
            response_text = tara_voice.process_command(command_text)
            tara_voice.speak(response_text) 

            tara_memory.log_event("tara_response", {"response": response_text, "exit_triggered": True})
            break # Exit the loop and end the program
            
        # Otherwise, process the command with Gemini
        response_text = tara_voice.process_command(command_text)
        tara_voice.speak(response_text)

        # Ensure we log every response TARA gives
        tara_memory.log_event("tara_response", {"response": response_text})


if __name__ == "__main__":
    main()
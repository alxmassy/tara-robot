# main.py

import os
from dotenv import load_dotenv # NEW: Import load_dotenv

from tara_core.voice_interface import VoiceInterface
from tara_core.assistant_tasks import AssistantTasks

# --- NEW: Load environment variables from .env file ---
load_dotenv()

# --- NEW: Get Gemini API Key from environment variable ---
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY") 

# Optional: Add a check for the API key, especially for hackathon demo robustness
if not GEMINI_API_KEY or GEMINI_API_KEY == "YOUR_GEMINI_API_KEY_HERE":
    print("ERROR: GEMINI_API_KEY not found or is still default. Please set it in your .env file or environment variables.")
    # For a hackathon, you might want to exit here or explicitly fall back to rule-based mode
    # For now, we'll let it proceed and VoiceInterface will handle the 'None' case.
    # exit(1) # Uncomment to exit if key is missing

def main():
    print("Starting TARA's core...")
    
    tara_assistant = AssistantTasks() # Initialize AssistantTasks first
    
    # Pass assistant_tasks instance and API key to VoiceInterface
    tara_voice = VoiceInterface(assistant_tasks=tara_assistant, gemini_api_key=GEMINI_API_KEY) 

    # Initial greeting from TARA
    tara_voice.speak("Hello there! I am TARA, your personal companion robot. How can I assist you today?")

    while True:
        # Listen for a command from the user (currently typed input)
        command_text = tara_voice.listen_for_command()
        
        # Use Gemini to process the command and get a conversational response
        response_text = tara_voice.process_command(command_text)

        # Check if the user explicitly asked to exit (e.g., "quit", "goodbye")
        # OR if Gemini's response contains clear exit phrases.
        lower_command_text = command_text.lower()
        lower_response_text = response_text.lower()

        if ("quit" in lower_command_text or 
            "exit" in lower_command_text or 
            "goodbye" in lower_command_text):
            # If the user explicitly asks to quit, we ensure TARA says goodbye
            # and then we exit. We don't rely solely on Gemini's exact wording.
            if not ("goodbye" in lower_response_text or "farewell" in lower_response_text):
                 tara_voice.speak("Goodbye! Have a wonderful day.") # Ensure a goodbye message is spoken
            else:
                 tara_voice.speak(response_text) # Speak Gemini's goodbye
            break # Exit the loop

        # Otherwise, just speak Gemini's response
        tara_voice.speak(response_text)

if __name__ == "__main__":
    main()
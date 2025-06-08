# main.py

from tara_core.voice_interface import VoiceInterface

def main():
    print("Starting TARA's core voice interface...")
    tara_voice = VoiceInterface()

    # Initial greeting from TARA
    tara_voice.speak("Hello there! I am TARA, your personal companion robot. How can I assist you today?")

    while True:
        # Listen for a command from the user (currently typed input)
        command = tara_voice.listen_for_command()
        
        # Process the command to determine intent and parameters
        intent, params = tara_voice.process_command(command)

        # Respond based on the detected intent
        if intent == "greet":
            tara_voice.speak("Hello to you too! It's nice to chat with you.")
        elif intent == "check_mood":
            tara_voice.speak("I am functioning optimally and ready to assist!")
        elif intent == "add_todo":
            item = params.get("item", "an item")
            tara_voice.speak(f"Okay, I'll remember to add '{item}' to your list.")
            # In Phase 2, this will call a function in assistant_tasks.py
        elif intent == "play_music":
            tara_voice.speak("Playing some soothing tunes for you.")
            # In Phase 2, this will call a function in assistant_tasks.py
        elif intent == "stop_music":
            tara_voice.speak("Music stopped.")
            # In Phase 2, this will call a function in assistant_tasks.py
        elif intent == "call_person":
            person = params.get("person", "someone")
            tara_voice.speak(f"Calling {person} now... (simulation)")
            # In Phase 2, this will call a function in assistant_tasks.py
        elif intent == "thank_you":
            tara_voice.speak("You're most welcome! It's my pleasure to help.")
        elif intent == "exit_program":
            tara_voice.speak("Goodbye! Have a wonderful day.")
            break # Exit the loop and end the program
        else:
            tara_voice.speak("I'm sorry, I didn't quite understand that. Could you rephrase?")

if __name__ == "__main__":
    main()
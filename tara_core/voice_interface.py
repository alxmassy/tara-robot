# tara_core/voice_interface.py

import os
import subprocess
from gtts import gTTS
import speech_recognition as sr
from pydub import AudioSegment
from pydub.playback import play

# --- IMPORTANT: Configure pydub to use ffmpeg ---
# Set the path to ffmpeg/ffplay if they are not in your system's PATH.
# In most WSL installations (and Raspberry Pi), they are in /usr/bin/
# These lines should be at the top level of the file, before any class definition.
AudioSegment.converter = "/usr/bin/ffmpeg"
AudioSegment.ffmpeg = "/usr/bin/ffmpeg"
AudioSegment.ffprobe = "/usr/bin/ffprobe"

class VoiceInterface:
    def __init__(self):
        # Initialize the recognizer for STT
        self.r = sr.Recognizer()
        print("VoiceInterface initialized.")

        # --- Optional: Check if ffmpeg/ffplay is available for pydub ---
        try:
            # Check for ffplay, which pydub uses for playback
            subprocess.run(["ffplay", "-version"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            print("ffplay detected for pydub playback.")
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("Warning: ffplay not found or not working. pydub might struggle without it.")
            print("Please ensure `ffmpeg` is installed (sudo apt install ffmpeg) in your WSL environment.")


    def speak(self, text, lang='en'):
        """
        Converts text to speech and plays it.
        Saves to a temporary file and plays using pydub.
        """
        print(f"TARA says: {text}") # Print for immediate feedback/mocking
        
        try:
            tts = gTTS(text=text, lang=lang, slow=False)
            audio_file = "temp_tara_audio.mp3"
            tts.save(audio_file)
            
            # Directly use pydub for playback, as it's proven to work
            song = AudioSegment.from_mp3(audio_file)
            play(song) # This uses the AudioSegment.converter/ffmpeg path configured above
            
            os.remove(audio_file) # Clean up the temporary file
        except Exception as e:
            print(f"Error during TTS: {e}")
            print("Common issues: Internet for gTTS, or `ffmpeg`/`ffplay` not installed/configured for pydub in WSL.")
            print("Also check: `pip install gTTS pydub`")


    def listen_for_command(self):
        """
        Listens for a command using the microphone (or mocks it via input for now).
        Returns the recognized text or None if unsuccessful.
        """
        print("\nTARA is listening (type your command and press Enter):")
        
        # --- MOCKING MIC INPUT FOR NOW (for hackathon/WSL demo) ---
        # Replace this with actual microphone input later when hardware is available
        user_input = input("You say: ")
        print("Processing...")
        return user_input.strip() # Return typed text for testing
        
        # --- UNCOMMENT BELOW WHEN YOU HAVE A MICROPHONE & READY TO TEST ---
        # try:
        #     with sr.Microphone() as source:
        #         self.r.adjust_for_ambient_noise(source) # Optional: adjust for ambient noise
        #         print("TARA: Say something!")
        #         audio = self.r.listen(source)
        #     
        #     print("TARA: Recognizing...")
        #     command = self.r.recognize_google(audio) # Using Google Web Speech API
        #     print(f"You said: {command}")
        #     return command
        # except sr.UnknownValueError:
        #     print("TARA could not understand audio. Please try again.")
        #     return None
        # except sr.RequestError as e:
        #     print(f"TARA: Could not request results from Google Speech Recognition service; {e}")
        #     print("Please check your internet connection.")
        #     return None
        # except Exception as e: # Catch other potential errors like no microphone
        #     print(f"Error during STT (Is microphone connected/configured?): {e}")
        #     print("Falling back to typed input for demonstration.")
        #     return input("You say (typed fallback): ").strip() # Fallback to typing if mic fails

    def process_command(self, command_text):
        """
        Processes the raw command text to determine intent and extract parameters.
        Returns (intent, parameters).
        """
        if command_text is None:
            return "unknown", {}

        command_text = command_text.lower() # Convert to lowercase for easier parsing

        # --- Basic Intent Recognition ---
        if "hello" in command_text or "hi tara" in command_text:
            return "greet", {}
        elif "how are you" in command_text:
            return "check_mood", {}
        elif "add" in command_text and ("to do" in command_text or "list" in command_text):
            # Example: "add take medicine to my to do list"
            parts = command_text.split("add ", 1)
            if len(parts) > 1:
                item_part = parts[1]
                # Further refine to remove common trailing phrases
                item = item_part.replace("to my to do list", "").replace("to my list", "").strip()
                item = item.replace("to do", "").strip() # Catches "add x to do"
                return "add_todo", {"item": item}
            return "add_todo", {"item": "something"} # Fallback if no item found
        elif "play music" in command_text or "play some music" in command_text:
            return "play_music", {}
        elif "stop music" in command_text:
            return "stop_music", {}
        elif "call" in command_text:
            # Example: "call mom"
            parts = command_text.split("call ", 1)
            if len(parts) > 1:
                person = parts[1].strip()
                return "call_person", {"person": person}
            return "call_person", {"person": "someone"} # Fallback if no person found
        elif "thank you" in command_text or "thanks" in command_text:
            return "thank_you", {}
        elif "quit" in command_text or "exit" in command_text or "goodbye" in command_text:
            return "exit_program", {}
        
        # Add more intents as you develop features
        
        return "unknown", {}
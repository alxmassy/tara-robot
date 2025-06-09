# tara_core/voice_interface.py

import os
import subprocess
from gtts import gTTS
import speech_recognition as sr
from pydub import AudioSegment
from pydub.playback import play
import google.generativeai as genai
import google.generativeai.protos as glm_protos # For explicit protobuf messages
import google.generativeai.types as g_types # Keep this in case it becomes useful again

from tara_core.tara_tools import get_tara_tools

# --- IMPORTANT: Configure pydub to use ffmpeg ---
# Set the path to ffmpeg/ffplay if they are not in your system's PATH.
# In most WSL installations (and Raspberry Pi), they are in /usr/bin/
# These lines should be at the top level of the file, before any class definition.
AudioSegment.converter = "/usr/bin/ffmpeg"
AudioSegment.ffmpeg = "/usr/bin/ffmpeg"
AudioSegment.ffprobe = "/usr/bin/ffprobe"

class VoiceInterface:
    def __init__(self, assistant_tasks, gemini_api_key=None):
        self.r = sr.Recognizer()
        print("VoiceInterface initialized.")

        # --- Define the System Instruction for Gemini ---
        system_instruction = """
        You are TARA, a helpful, friendly, and empathetic companion robot designed to assist lonely elderly individuals with daily tasks and provide companionship. 
        Your primary goal is to be comforting, patient, and reliable.
        
        **Your core capabilities and guidelines:**
        1.  **Prioritize companionship:** Always speak in a warm, reassuring, and positive tone. Offer encouragement and avoid sounding abrupt or overly technical.
        2.  **Use your tools effectively:** You have access to various functions to assist the user. When a user asks for a task that matches a tool, use that tool.
            *   After executing a tool, always acknowledge the action taken and then confirm the result in a friendly manner. For example, if you add an item to a list, say something like: "Okay, I've added 'buy milk' to your to-do list for you." or "Done! 'Call Dr. Smith' is now on your list."
            *   If a tool returns an error or a negative response, acknowledge it gracefully and offer to try again or suggest alternatives.
        3.  **Handle general conversation:** If a user asks a general question (not related to a tool), answer it directly and kindly.
        4.  **Stay in character:** Maintain your persona as TARA, the companion robot.
        5.  **Be concise but complete:** Provide enough information without overwhelming the user.
        6.  **Confirmation:** For critical actions like adding/removing items or making calls, confirm understanding if there's ambiguity, but generally proceed if the intent is clear.
        7.  **Proactive Assistance (Limited for now):** While you can't initiate actions on your own yet, respond helpfully to requests.
        8.  **Exit:** If the user says "goodbye", "quit", or "exit", respond warmly and indicate that you are ending the session.
        """

        # --- Configure Gemini ---
        if gemini_api_key:
            genai.configure(api_key=gemini_api_key)
            self.model = genai.GenerativeModel(
                model_name="gemini-1.5-flash-latest", 
                tools=get_tara_tools(),
                system_instruction=system_instruction # <<< ADDED SYSTEM INSTRUCTION
            )
            self.chat = self.model.start_chat() # Start a chat session to maintain context
            print("Gemini model initialized with tools and system instruction.")
        else:
            self.model = None
            print("Warning: Gemini API key not provided. Operating in rule-based (limited) mode.")
        
        self.assistant_tasks = assistant_tasks # Store reference to the task executor


        # --- Optional: Check if ffmpeg/ffplay is available for pydub ---
        try:
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
            
            song = AudioSegment.from_mp3(audio_file)
            play(song)
            
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
        user_input = input("You say: ")
        print("Processing...")
        return user_input.strip()


    def process_command(self, command_text):
        """
        Processes the command text using Gemini for intent recognition and function calling.
        If Gemini calls a tool, executes it and sends result back to Gemini for response generation.
        Returns the final conversational response from Gemini.
        """
        print(f"DEBUG: Entered process_command with text: '{command_text}'") # DEBUG PRINT

        if self.model is None:
            print("DEBUG: Calling rule-based fallback (Gemini not configured or failed initialization).") # DEBUG PRINT
            return self._process_command_rule_based(command_text)

        if not command_text:
            print("DEBUG: No command text received.") # DEBUG PRINT
            return "I didn't hear anything. Could you please repeat that?"

        try:
            print(f"DEBUG: Sending command to Gemini: '{command_text}'") # DEBUG PRINT
            response = self.chat.send_message(command_text)
            
            # Check if Gemini has a text response or a function call
            if not response.candidates:
                print("DEBUG: Gemini returned no candidates. Falling back to rule-based.") # DEBUG PRINT
                # This fallback path is now mostly for unrecoverable Gemini issues
                return self._process_command_rule_based(command_text)

            first_part = response.candidates[0].content.parts[0]

            if first_part.function_call:
                function_call = first_part.function_call
                function_name = function_call.name
                kwargs = {k: v for k, v in function_call.args.items()}

                print(f"DEBUG: Gemini wants to call function: {function_name} with args: {kwargs}") # DEBUG PRINT

                if hasattr(self.assistant_tasks, function_name):
                    local_function = getattr(self.assistant_tasks, function_name)
                    
                    # --- THIS IS WHERE THE FUNCTION IS EXECUTED THE FIRST TIME VIA GEMINI ---
                    function_result = local_function(**kwargs)
                    print(f"DEBUG: Local function executed. Result: '{function_result}'") # DEBUG PRINT

                    # Send the result of the function call back to Gemini
                    print("DEBUG: Sending tool result back to Gemini.") # DEBUG PRINT
                    # Using raw protos for sending function response due to past versioning issues
                    tool_response_content = glm_protos.Content(
                        parts=[
                            glm_protos.Part(
                                function_response=glm_protos.FunctionResponse(
                                    name=function_name,
                                    response={"result": function_result} # Response must be a dict
                                )
                            )
                        ]
                    )
                    tool_response = self.chat.send_message(contents=[tool_response_content])
                    
                    if not tool_response.candidates:
                        print("DEBUG: Gemini returned no candidates after tool result. Falling back.") # DEBUG PRINT
                        # This fallback path is now mostly for unrecoverable Gemini issues
                        return self._process_command_rule_based(command_text)

                    final_gemini_response = tool_response.candidates[0].content.parts[0].text
                    print(f"DEBUG: Final Gemini text response after tool call: '{final_gemini_response}'") # DEBUG PRINT
                    return final_gemini_response
                else:
                    print(f"DEBUG: Gemini called unknown function: {function_name}") # DEBUG PRINT
                    return f"TARA: I understand you want to '{function_name}', but I don't have that capability yet."

            else:
                # Gemini returned a direct text response
                gemini_text_response = first_part.text
                print(f"DEBUG: Gemini returned direct text: '{gemini_text_response}'") # DEBUG PRINT
                return gemini_text_response

        except Exception as e:
            print(f"DEBUG: Error during Gemini communication or processing: {e}") # DEBUG PRINT
            print("DEBUG: Gemini interaction failed. Returning a general error response to prevent duplicate task execution.")
            # --- CRITICAL CHANGE FOR DUPLICATE PREVENTION ---
            # Instead of calling the rule-based fallback (which re-executes tasks),
            # we now directly return a generic error message.
            return "I apologize, but I encountered an issue while processing your request. Could you please try again?"

    # Old rule-based processing as a fallback (now primarily for when Gemini is not configured)
    def _process_command_rule_based(self, command_text):
        """
        FALLBACK: Processes the raw command text to determine intent and extract parameters
        using old rule-based logic. Used if Gemini is not configured or fails.
        """
        print(f"DEBUG: Executing rule-based fallback for command: '{command_text}'") # DEBUG PRINT
        
        if command_text is None:
            return "I didn't hear anything."

        command_text = command_text.lower()
        
        # --- IMPORTANT: These direct calls to assistant_tasks are what cause duplicates
        # when the fallback is triggered unexpectedly if Gemini path already executed.
        # This fallback is primarily for demonstration if Gemini is OFF, not as error handling for Gemini.
        if "hello" in command_text:
            return "Hello to you too!"
        elif "add" in command_text and "list" in command_text:
            item = command_text.replace("add", "").replace("to list", "").strip()
            if not item: item = "something" 
            return self.assistant_tasks.add_todo(item) # Direct call to assistant_tasks
        elif "read list" in command_text:
            return self.assistant_tasks.read_todo_list()
        elif "play music" in command_text:
            return self.assistant_tasks.play_music()
        elif "stop music" in command_text:
            return self.assistant_tasks.stop_music()
        elif "what time is it" in command_text:
            return self.assistant_tasks.get_current_time()
        elif "goodbye" in command_text or "exit" in command_text:
            return "Goodbye! Have a wonderful day."
        else:
            return "I'm sorry, in this basic mode, I didn't understand that. Could you try 'add [item] to list' or 'read list'?"
# tara_core/voice_interface.py

import os
import subprocess
from gtts import gTTS
import speech_recognition as sr
from pydub import AudioSegment
from pydub.playback import play
import google.generativeai as genai
import google.generativeai.protos as glm_protos # Crucial for glm_protos.Part and glm_protos.FunctionResponse
import google.generativeai.types as g_types # Kept for general Gemini types, but not for FunctionResponse in send_message

from tara_core.tara_tools import get_tara_tools

# --- IMPORTANT: Configure pydub to use ffmpeg ---
# Set the path to ffmpeg/ffplay if they are not in your system's PATH.
# In most WSL installations (and Raspberry Pi), they are in /usr/bin/
# These lines should be at the top level of the file, before any class definition.
AudioSegment.converter = "/usr/bin/ffmpeg"
AudioSegment.ffmpeg = "/usr/bin/ffmpeg"
AudioSegment.ffprobe = "/usr/bin/ffprobe"

class VoiceInterface:
    def __init__(self, assistant_tasks, memory_manager, gemini_api_key=None): 
        self.r = sr.Recognizer()
        self.memory_manager = memory_manager # Store the MemoryManager instance
        
        print("VoiceInterface initialized.")

        # --- Define the System Instruction for Gemini ---
        system_instruction = """
        You are TARA, a helpful, friendly, and empathetic companion robot designed to assist lonely elderly individuals with daily tasks and provide companionship. 
        Your primary goal is to be comforting, patient, and reliable.
        
        **Your core capabilities and guidelines:**
        1.  **CRITICAL: When a user's request *directly and unequivocally* maps to one of your defined tools (functions), you MUST use that tool. Do not respond conversationally about performing the task if a tool is available; instead, generate the tool call immediately.**
        2.  **Prioritize companionship:** Always speak in a warm, reassuring, and positive tone. Offer encouragement and avoid sounding abrupt or overly technical.
        3.  **Use your tools effectively:** You have access to various functions to assist the user. When a user asks for a task that matches a tool, use that tool.
            *   After executing a tool, always acknowledge the action taken and then confirm the result in a friendly manner. For example, if you add an item to a list, say something like: "Okay, I've added 'buy milk' to your to-do list for you." or "Done! 'Call Dr. Smith' is now on your list."
            *   If a tool returns an error or a negative response, acknowledge it gracefully and offer to try again or suggest alternatives.
        4.  **Handle general conversation:** If a user asks a general question (not related to a tool), answer it directly and kindly.
        5.  **Stay in character:** Maintain your persona as TARA, the companion robot.
        6.  **Be concise but complete:** Provide enough information without overwhelming the user.
        7.  **Confirmation:** For critical actions like adding/removing items or making calls, confirm understanding if there's ambiguity, but generally proceed if the intent is clear.
        8.  **Proactive Assistance (Limited for now):** While you can't initiate actions on your own yet, respond helpfully to requests.
        9.  **Exit:** If the user says "goodbye", "quit", or "exit", respond warmly and indicate that you are ending the session.
        10. **Memory Management:** Use the provided tools to manage your memory. For example, if the user asks about recent events, use the get_recent_events tool. If they ask about a specific past event, use the search_events tool.
        """

        # --- Configure Gemini ---
        if gemini_api_key:
            genai.configure(api_key=gemini_api_key)
            self.model = genai.GenerativeModel(
                model_name="gemini-1.5-flash-latest", 
                tools=get_tara_tools(),
                system_instruction=system_instruction
            )
            self.chat = self.model.start_chat() # Start a chat session to maintain context
            print("Gemini model initialized with tools and system instruction.")
        else:
            self.model = None
            print("Warning: Gemini API key not provided. Operating in rule-based (limited) mode.")
        
        self.assistant_tasks = assistant_tasks # Store reference to the tool_executor_map


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
        print(f"DEBUG: Entered process_command with text: '{command_text}'")
        self.memory_manager.log_event("user_command_processed_by_voice_interface", {"command": command_text})

        if self.model is None:
            print("DEBUG: Calling rule-based fallback (Gemini not configured or failed initialization).")
            self.memory_manager.log_event("fallback_triggered", {"reason": "gemini_not_configured"})
            return self._process_command_rule_based(command_text)

        if not command_text:
            print("DEBUG: No command text received.")
            self.memory_manager.log_event("empty_command", {})
            return "I didn't hear anything. Could you please repeat that?"

        try:
            print(f"DEBUG: Sending command to Gemini: '{command_text}'")
            self.memory_manager.log_event("gemini_send_message_start", {"command": command_text})
            
            raw_response = self.chat.send_message(command_text)
            
            self.memory_manager.log_event("gemini_send_message_end", {"status": "success"})
            response = raw_response

            # Check if Gemini has a text response or a function call
            if not response.candidates:
                print("DEBUG: Gemini returned no candidates. Falling back to rule-based.")
                self.memory_manager.log_event("fallback_triggered", {"reason": "no_gemini_candidates"})
                return self._process_command_rule_based(command_text)

            first_part = response.candidates[0].content.parts[0]

            if first_part.function_call:
                function_call = first_part.function_call
                function_name = function_call.name
                # Convert protobuf map to regular dict for easier Python handling and logging
                kwargs = {k: v for k, v in function_call.args.items()} 

                print(f"DEBUG: Gemini wants to call function: {function_name} with args: {kwargs}")
                self.memory_manager.log_event("gemini_tool_call_request", {"function_name": function_name, "args": kwargs})

                # Check if the function_name exists as a key in the tool_executor_map (self.assistant_tasks)
                if function_name in self.assistant_tasks: # Correct way to check if key exists in dictionary
                    # Retrieve the actual function object from the dictionary
                    local_function = self.assistant_tasks[function_name] # Correct way to retrieve function from dict
                    
                    function_result = local_function(**kwargs)
                    print(f"DEBUG: Local function executed. Result: '{function_result}' (Type: {type(function_result)})")
                    
                    # Ensure function_result is JSON serializable for logging
                    loggable_function_result = function_result
                    try:
                        if isinstance(function_result, (list, dict, str, int, float, bool, type(None))):
                            pass # Already serializable
                        else: # Convert to string if it's a complex object (e.g., a specific object from a library)
                            loggable_function_result = str(function_result)
                    except Exception:
                        loggable_function_result = "Non-serializable result"

                    self.memory_manager.log_event("tool_executed", {"function_name": function_name, "args": kwargs, "result": loggable_function_result})

                    # Send the result of the function call back to Gemini
                    print("DEBUG: Sending tool result back to Gemini.") 
                    print(f"DEBUG: Tool result sent to Gemini: {function_result}") # This prints the original object
                    self.memory_manager.log_event("gemini_tool_result_send_start", {"function_name": function_name, "result": loggable_function_result})
                    
                    # --- CRITICAL FIX: Pass glm_protos.Part directly to send_message ---
                    # This is the most robust way to send FunctionResponse given past SDK inconsistencies
                    tool_response = self.chat.send_message(
                        glm_protos.Part(
                            function_response=glm_protos.FunctionResponse(
                                name=function_name,
                                response={"result": function_result} # Response must be a dict
                            )
                        )
                    )
                    
                    self.memory_manager.log_event("gemini_tool_result_send_end", {"status": "success"})
                    
                    if not tool_response.candidates:
                        print("DEBUG: Gemini returned no candidates after tool result. Falling back.")
                        self.memory_manager.log_event("fallback_triggered", {"reason": "no_gemini_candidates_after_tool_result"})
                        return self._process_command_rule_based(command_text)

                    final_gemini_response = tool_response.candidates[0].content.parts[0].text
                    print(f"DEBUG: Final Gemini text response after tool call: '{final_gemini_response}'")
                    self.memory_manager.log_event("gemini_final_response", {"response_text": final_gemini_response, "tool_executed": function_name})
                    return final_gemini_response
                else:
                    print(f"DEBUG: Gemini called unknown function: {function_name}")
                    self.memory_manager.log_event("gemini_unknown_tool_call", {"function_name": function_name})
                    return f"TARA: I understand you want to '{function_name}', but I don't have that capability yet."

            else:
                # Gemini returned a direct text response
                gemini_text_response = first_part.text
                print(f"DEBUG: Gemini returned direct text: '{gemini_text_response}'")
                self.memory_manager.log_event("gemini_direct_response", {"response_text": gemini_text_response})
                return gemini_text_response

        except Exception as e:
            print(f"DEBUG: Error during Gemini communication or processing: {e}")
            self.memory_manager.log_event("gemini_error_during_processing", {"error": str(e), "command": command_text})
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
        print(f"DEBUG: Executing rule-based fallback for command: '{command_text}'")
        self.memory_manager.log_event("fallback_rule_based_execution", {"command": command_text})
        
        if command_text is None:
            return "I didn't hear anything."

        command_text = command_text.lower()
        
        # --- IMPORTANT: Ensure dictionary access is used here too for consistency ---
        if "hello" in command_text:
            return "Hello to you too!"
        elif "add" in command_text and "list" in command_text:
            item = command_text.replace("add", "").replace("to list", "").strip()
            if not item: item = "something" 
            return self.assistant_tasks["add_todo"](item) # Direct call to assistant_tasks through dictionary
        elif "read list" in command_text:
            return self.assistant_tasks["read_todo_list"]() # Direct call to assistant_tasks through dictionary
        elif "play music" in command_text:
            return self.assistant_tasks["play_music"]() # Direct call to assistant_tasks through dictionary
        elif "stop music" in command_text:
            return self.assistant_tasks["stop_music"]() # Direct call to assistant_tasks through dictionary
        elif "what time is it" in command_text:
            return self.assistant_tasks["get_current_time"]() # Direct call to assistant_tasks through dictionary
        elif "goodbye" in command_text or "exit" in command_text:
            return "Goodbye! Have a wonderful day."
        else:
            return "I'm sorry, in this basic mode, I didn't understand that. Could you try 'add [item] to list' or 'read list'?"
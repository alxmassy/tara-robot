# tara_core/assistant_tasks.py

import json
import os
import datetime # Added for get_current_time

# Define a path for the persistent data files
DATA_DIR = "tara_data"
TODO_FILE = os.path.join(DATA_DIR, "todo_list.json")

class AssistantTasks:
    def __init__(self):
        # Ensure the data directory exists
        os.makedirs(DATA_DIR, exist_ok=True)
        print("AssistantTasks initialized.")

    def _load_todo_list(self):
        """Loads the to-do list from a JSON file."""
        if not os.path.exists(TODO_FILE):
            return []
        try:
            with open(TODO_FILE, 'r') as f:
                return json.load(f)
        except json.JSONDecodeError:
            print(f"Warning: Corrupted {TODO_FILE}. Starting with an empty list.")
            # Optionally, you could back up the corrupted file before overwriting
            return []
        except Exception as e:
            print(f"Error loading todo list: {e}")
            return []

    def _save_todo_list(self, todo_list):
        """Saves the to-do list to a JSON file."""
        try:
            with open(TODO_FILE, 'w') as f:
                json.dump(todo_list, f, indent=4)
        except Exception as e:
            print(f"Error saving todo list: {e}")


    def add_todo(self, item):
        """Adds an item to the to-do list."""
        if not item or item.lower() == "something": # Prevent adding "something" or empty items
            return "I need a specific item to add. What would you like to add?"
        
        todo_list = self._load_todo_list()
        todo_list.append(item)
        self._save_todo_list(todo_list)
        return f"Okay, I've added '{item}' to your to-do list."

    def read_todo_list(self):
        """Reads out the current to-do list."""
        todo_list = self._load_todo_list()
        if not todo_list:
            return "Your to-do list is empty."
        
        if len(todo_list) == 1:
            return f"You have one item on your list: {todo_list[0]}."
        
        # Nicely format the list for speech
        items_str = ", ".join(todo_list[:-1]) + f", and {todo_list[-1]}" if len(todo_list) > 1 else todo_list[0]
        return f"You have {len(todo_list)} items on your list: {items_str}."

    def remove_todo(self, item_keyword):
        """Removes an item from the to-do list based on a keyword."""
        if not item_keyword:
            return "Please tell me what item you'd like to remove."
        
        todo_list = self._load_todo_list()
        original_length = len(todo_list)
        
        # Create a new list excluding items that contain the keyword (case-insensitive)
        removed_items = []
        new_todo_list = []
        for todo_item in todo_list:
            if item_keyword.lower() not in todo_item.lower():
                new_todo_list.append(todo_item)
            else:
                removed_items.append(todo_item)

        if len(new_todo_list) < original_length:
            self._save_todo_list(new_todo_list)
            if len(removed_items) == 1:
                return f"I've removed '{removed_items[0]}' from your list."
            else:
                return f"I've removed {len(removed_items)} items from your list, including those related to '{item_keyword}'."
        else:
            return f"I couldn't find any item containing '{item_keyword}' on your list."

    # --- Music Related Functions (Mocked) ---
    def play_music(self, genre=None):
        """Simulates playing music."""
        if genre:
            return f"Certainly, playing some {genre} music for you."
        else:
            return "Certainly, playing some soothing music for you."

    def stop_music(self):
        """Simulates stopping music."""
        return "Music stopped."
    
    def next_song(self):
        """Simulates playing the next song."""
        return "Playing the next song."

    # --- Calling Related Functions (Mocked) ---
    def call_person(self, person_name):
        """Simulates calling a person."""
        if not person_name or person_name.lower() == "someone":
            return "Who would you like me to call?"
        return f"Attempting to call {person_name} now... (simulation complete)."

    def send_message(self, person_name, message):
        """Simulates sending a message."""
        if not person_name or person_name.lower() == "someone":
            return "Who should I send the message to?"
        if not message or message.lower() == "empty message":
            return "What message would you like to send?"
        return f"Sending message to {person_name}: '{message}'... (simulation complete)."

    # --- Reminder Related Functions (Mocked for now, will be more complex later) ---
    def set_reminder(self, time, message):
        """Simulates setting a reminder."""
        if not time or not message:
            return "I need both a time and a message for the reminder."
        return f"Okay, I've set a reminder for {time}: '{message}'."

    def get_current_time(self):
        """Gets the current time."""
        now = datetime.datetime.now()
        return f"The current time is {now.strftime('%I:%M %p')}"
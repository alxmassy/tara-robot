def get_tara_tools():
    """
    Defines the functions (tools) that TARA can use,
    in a format understood by Google Gemini.
    """
    return [
        {
            "function_declarations": [
                {
                    "name": "add_todo",
                    "description": "Adds a specific item to the user's to-do list.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "item": {"type": "string", "description": "The item to add to the to-do list (e.g., 'buy milk', 'call doctor')."}
                        },
                        "required": ["item"]
                    }
                },
                {
                    "name": "read_todo_list",
                    "description": "Reads out all items currently on the user's to-do list.",
                    "parameters": {
                        "type": "object",
                        "properties": {} # No parameters needed
                    }
                },
                 {
                    "name": "remove_todo",
                    "description": "Removes an item from the to-do list based on a keyword or phrase.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "item_keyword": {"type": "string", "description": "A keyword or phrase identifying the item to remove (e.g., 'milk', 'doctor appointment')."}
                        },
                        "required": ["item_keyword"]
                    }
                },
                {
                    "name": "play_music",
                    "description": "Starts playing music. Can optionally specify a genre.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "genre": {"type": "string", "description": "The genre of music to play (e.g., 'jazz', 'classical', 'pop'). Optional.", "nullable": True}
                        },
                    }
                },
                {
                    "name": "stop_music",
                    "description": "Stops any currently playing music.",
                    "parameters": {
                        "type": "object",
                        "properties": {}
                    }
                },
                {
                    "name": "next_song",
                    "description": "Plays the next song in the queue or playlist.",
                    "parameters": {
                        "type": "object",
                        "properties": {}
                    }
                },
                {
                    "name": "call_person",
                    "description": "Initiates a simulated phone call to a specified person.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "person_name": {"type": "string", "description": "The name of the person to call (e.g., 'Mom', 'Doctor Smith')."}
                        },
                        "required": ["person_name"]
                    }
                },
                {
                    "name": "send_message",
                    "description": "Sends a simulated text message to a specified person with a given message content.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "person_name": {"type": "string", "description": "The name of the person to send the message to."},
                            "message": {"type": "string", "description": "The content of the message to send."}
                        },
                        "required": ["person_name", "message"]
                    }
                },
                {
                    "name": "set_reminder",
                    "description": "Sets a reminder for the user at a specified time with a given message.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "time": {"type": "string", "description": "The time for the reminder (e.g., '3 PM', 'tomorrow morning')."},
                            "message": {"type": "string", "description": "The content of the reminder (e.g., 'take medicine')."}
                        },
                        "required": ["time", "message"]
                    }
                },
                {
                    "name": "get_current_time",
                    "description": "Retrieves the current local time.",
                    "parameters": {
                        "type": "object",
                        "properties": {}
                    }
                }
            ]
        }
    ]
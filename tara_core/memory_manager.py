# tara_core/memory_manager.py

import json
import os
from datetime import datetime

MEMORY_FILE = os.path.join("tara_data", "memory_log.jsonl") # JSON Lines file

class MemoryManager:
    def __init__(self):
        os.makedirs("tara_data", exist_ok=True) # Ensure data directory exists
        print("MemoryManager initialized.")

    def log_event(self, event_type, data):
        """
        Logs an event to the memory file.
        Args:
            event_type (str): Category of the event (e.g., "user_command", "tool_call", "tara_response").
            data (dict): A dictionary containing relevant information for the event.
        """
        event = {
            "timestamp": datetime.now().isoformat(),
            "type": event_type,
            "data": data
        }
        try:
            with open(MEMORY_FILE, 'a') as f:
                f.write(json.dumps(event) + '\n')
            print(f"DEBUG(Memory): Logged event: {event_type}") # MODIFIED DEBUG PRINT
        except Exception as e:
            print(f"ERROR(Memory): Failed to log event: {e}") # MODIFIED DEBUG PRINT

    def get_recent_events(self, count=5):
        """Retrieves the most recent events from the log."""
        events = []
        if not os.path.exists(MEMORY_FILE):
            print("DEBUG(Memory): Memory file does not exist, returning empty list.") # NEW DEBUG
            return []
        try:
            with open(MEMORY_FILE, 'r') as f:
                for line in f:
                    try:
                        events.append(json.loads(line))
                    except json.JSONDecodeError as e:
                        print(f"WARNING(Memory): Corrupted memory log line skipped: {e} - Line: {line.strip()}") # MODIFIED DEBUG
            
            count = int(count) if isinstance(count, (int, float)) and count > 0 else 5
            recent_events = events[-count:]
            print(f"DEBUG(Memory): get_recent_events returning {len(recent_events)} events: {recent_events}") # NEW DEBUG
            return recent_events
        except Exception as e:
            print(f"ERROR(Memory): Error reading memory file for recent events: {e}") # MODIFIED DEBUG
            return []

    def search_events(self, query_keywords, limit=10):
        """
        Searches the event log for events matching query_keywords.
        This is a very basic keyword search for demo.
        """
        matching_events = []
        if not os.path.exists(MEMORY_FILE):
            print("DEBUG(Memory): Memory file does not exist for search, returning empty list.") # NEW DEBUG
            return []
        try:
            limit = int(limit) if isinstance(limit, (int, float)) and limit > 0 else 10
            with open(MEMORY_FILE, 'r') as f:
                for line in f:
                    try:
                        event = json.loads(line)
                        event_str = json.dumps(event).lower()
                        if any(keyword.lower() in event_str for keyword in query_keywords):
                            matching_events.append(event)
                            if len(matching_events) >= limit:
                                break
                    except json.JSONDecodeError as e:
                        print(f"WARNING(Memory): Corrupted memory log line skipped during search: {e} - Line: {line.strip()}") # MODIFIED DEBUG
            
            print(f"DEBUG(Memory): search_events returning {len(matching_events)} events for keywords {query_keywords}: {matching_events}") # NEW DEBUG
            return matching_events
        except Exception as e:
            print(f"ERROR(Memory): Error reading memory file for search: {e}") # MODIFIED DEBUG
            return []
import os
import google.generativeai as genai

# Replace with your actual API key or ensure it's in your environment variables
# For hackathon, placing it directly here is okay for quick testing, but ideally use os.environ.get
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "YOUR_GEMINI_API_KEY_HERE") 

if GEMINI_API_KEY == "YOUR_GEMINI_API_KEY_HERE":
    print("ERROR: Please set your GEMINI_API_KEY environment variable or replace the placeholder in this script.")
    exit()

genai.configure(api_key=GEMINI_API_KEY)

print("Available Gemini Models:")
for m in genai.list_models():
    if 'generateContent' in m.supported_generation_methods:
        print(f"- {m.name} (Supports generateContent)")
    else:
        print(f"- {m.name} (Does NOT support generateContent)")

print("\nIf 'gemini-pro' or 'gemini-1.0-pro' is not listed, there might be a regional access issue or a temporary API problem.")

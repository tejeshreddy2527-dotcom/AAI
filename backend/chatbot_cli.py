"""
CLI Chatbot in the backend directory.
"""
import sys
import os

# Delegate to root chatbot.py logic or standalone
from server import call_gemini_api, load_env_file, DEFAULT_MODEL

def main():
    load_env_file()
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        api_key = input("Enter your Gemini API Key: ").strip()
        if not api_key:
            print("API Key required. Exiting.")
            sys.exit(1)

    history = []
    print("\n--- Gemini Backend CLI Chat ---")
    print("Type 'exit' to quit.\n")
    while True:
        try:
            msg = input("You: ").strip()
            if not msg:
                continue
            if msg.lower() in ("exit", "quit"):
                break
            history.append({"role": "user", "parts": [{"text": msg}]})
            reply = call_gemini_api(api_key, history)
            history.append({"role": "model", "parts": [{"text": reply}]})
            print(f"Gemini: {reply}\n")
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"Error: {e}\n")

if __name__ == "__main__":
    main()

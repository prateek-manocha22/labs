import os
import requests
from dotenv import load_dotenv

# 1. Load your API keys from a .env file
load_dotenv()
API_KEY = os.getenv("OPENAI_API_KEY")

def simple_chat(user_prompt):
    """A minimal script to get a response from an LLM."""
    
    # The standard OpenAI-compatible endpoint structure
    url = "https://api.openai.com/v1/chat/completions"
    
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "gpt-4o-mini",
        "messages": [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": user_prompt}
        ]
    }

    print(f"Sending prompt: {user_prompt}...")
    
    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status() # Raise error if request failed
        
        result = response.json()
        content = result['choices'][0]['message']['content']
        return content
        
    except Exception as e:
        return f"Error: {str(e)}"

if __name__ == "__main__":
    if not API_KEY:
        print("❌ Error: OPENAI_API_KEY not found in environment.")
        print("Please create a .env file with OPENAI_API_KEY=your_key")
    else:
        answer = simple_chat("What are the 3 laws of robotics?")
        print("\n--- Model Response ---")
        print(answer)

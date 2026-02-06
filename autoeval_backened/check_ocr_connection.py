
import os
import google.generativeai as genai
from dotenv import load_dotenv

def test_connection():
    load_dotenv()
    api_key = os.getenv("GEMINI_API_KEY")
    
    if not api_key:
        print("FAIL: No API Key found in environment.")
        return

    print(f"DEBUG: Key found (starts with {api_key[:5]}...)")
    
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-1.5-flash")
        
        # Simple generation test
        response = model.generate_content("Reply with 'OK' if you see this.")
        
        print("\n" + "="*40)
        print("CONNECTION TEST RESULT")
        print("="*40)
        print(f"Response: {response.text.strip()}")
        print("STATUS: SUCCESS")
        
    except Exception as e:
        print("\n" + "="*40)
        print("CONNECTION TEST RESULT")
        print("="*40)
        print(f"Error: {str(e)}")
        print("STATUS: FAILED")

if __name__ == "__main__":
    test_connection()

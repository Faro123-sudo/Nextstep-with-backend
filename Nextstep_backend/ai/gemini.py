import json
import os
from pathlib import Path
from dotenv import load_dotenv
from google import genai
from typing import Dict, Any, List

# --- API KEY & CLIENT SETUP ---
# Load environment variables once
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / '.env')
# The API key is loaded into the environment, which the client will auto-detect.
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

# Initialize the Gemini client
try:
    client = genai.Client()
    MODEL = "gemini-2.5-flash"
except Exception as e:
    print(f"Error initializing Gemini client: {e}")
    client = None 

def format_user_responses_for_llm(user_history: Dict[str, List[Dict[str, str]]]) -> str:
    """
    Converts the structured user response dictionary into a single, clean list 
    of "Question: Answer" pairs, which is less likely to confuse the LLM.
    """
    if not user_history or 'responses' not in user_history:
        return "No user responses provided."

    profile_parts = []
    for item in user_history['responses']:
        question = item.get("question", "Unknown Question").strip()
        answer = item.get("answer", "No Answer").strip()
        # Use a simple comma and space separator to avoid complex newlines/formatting
        profile_parts.append(f"{question}: {answer}")
        
    return "; ".join(profile_parts)


# --- GEMINI API INITIALIZATION AND CALL FUNCTION ---
def get_gemini_recommendations(user_history: Dict[str, Any]) -> List[Dict[str, str]]:
    """
    Sends the user's quiz responses to the Gemini API to receive structured 
    career recommendations.
    """
    if not client:
        raise Exception("Gemini client failed to initialize.")
    
    # 1. Format the user history into a clean, single line string
    user_profile_string = format_user_responses_for_llm(user_history)
    
    # 2. Define the structured prompt (more assertive)
    career_prompt = (
        "You are a professional career counselor. Analyze the user's profile based on their quiz answers. "
        "Recommend exactly 3 distinct, suitable career paths. Your output MUST be a JSON array "
        "of objects as defined by the schema, and nothing else. "
        f"User Profile Summary: {user_profile_string}"
    )
    
    # 3. Define the JSON Schema for structured output
    career_schema = {
        "type": "array",
        "items": {
            "type": "object",
            "properties": {
                "career": {
                    "type": "string",
                    "description": "The specific title of the recommended career."
                },
                "reason": {
                    "type": "string",
                    "description": "A 2-3 sentence explanation of why this career aligns with the user's quiz answers."
                }
            },
            "required": ["career", "reason"]
        }
    }
    
    # 4. Call the Gemini API with the full prompt and config
    response = client.models.generate_content(
        model=MODEL,
        contents=career_prompt,
        config={
            "response_mime_type": "application/json",
            "response_schema": career_schema
        }
    )    # 5. Parse the structured JSON response
    try:
        # json.loads converts the JSON string into a Python list/dictionary
        recommendations = json.loads(response.text)
        return recommendations
    except json.JSONDecodeError:
        print("\n--- JSON DECODE ERROR ---")
        print("Failed to decode JSON. Check model's raw response for fragmentation:")
        print(response.text)
        print("--------------------------")
        return []
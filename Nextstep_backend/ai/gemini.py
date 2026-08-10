import json
import os
from pathlib import Path
from dotenv import load_dotenv
from typing import Dict, Any, List

# --- API KEY & CLIENT SETUP ---
# Load environment variables once
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / '.env')
# The API key is loaded into the environment, which the client will auto-detect.
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

# Initialize the Gemini client
client = None
MODEL = "gemini-2.5-flash"
try:
    from google import genai
    client = genai.Client()
except Exception as e:
    print(f"Error initializing Gemini client: {e}")
    print("Gemini API features will not be available") 

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





def get_career_recommendation(career_data: Dict[str, Any], user_type: str = None) -> Dict[str, str]:
    """
    Generates a single career recommendation based on a specific career the user is viewing.
    Retries up to 3 times to get a valid, available YouTube video.

    Args:
        career_data: Dictionary containing career information (name, description, skills, etc.)
        user_type: Optional user type (e.g., 'student', 'professional') for personalization

    Returns:
        Dictionary with 'recommendation', 'relatedCareer', and 'resourceUrl' keys.
        'resourceUrl' will be empty string if no available video could be found.
    """
    if not client:
        raise Exception("Gemini client failed to initialize.")

    # Format career info for the prompt
    career_name = career_data.get('careerName', 'Unknown Career')
    description = career_data.get('description', '')
    skills = career_data.get('skillsRequired', [])
    industry = career_data.get('industry', 'Unknown')

    skills_str = ", ".join(skills) if skills else "Not specified"
    user_context = f"for a {user_type}" if user_type else ""

    # Define the JSON Schema for structured output
    recommendation_schema = {
        "type": "object",
        "properties": {
            "recommendation": {
                "type": "string",
                "description": "A 2-3 sentence insight about the career viewed."
            },
            "relatedCareer": {
                "type": "string",
                "description": "A single related career that builds on similar skills."
            },
            "resourceUrl": {
                "type": "string",
                "description": "A YouTube embed URL in the format https://www.youtube.com/embed/VIDEO_ID for a relevant tutorial or career overview video."
            }
        },
        "required": ["recommendation", "relatedCareer", "resourceUrl"]
    }

    recommendation = None
    last_error = None
    verified = False  # True once a video passes the oEmbed check

    # Pre-seed with known joke/placeholder video IDs that Gemini tends to hallucinate
    BLACKLISTED_IDS = {"dQw4w9WgXcQ", "oHg5SJYRHA0", "9bZkp7q19f0"}  # Rick Roll + common placeholders
    invalid_ids = list(BLACKLISTED_IDS)
    MAX_RETRIES = 1  # Keep low to preserve free-tier Gemini quota

    for attempt in range(1, MAX_RETRIES + 1):
        # Build the prompt, adding exclusions on retries
        exclusion_note = ""
        if invalid_ids:
            exclusion_note = (
                f" The following video IDs did NOT work and must NOT be used: {', '.join(invalid_ids)}."
                " Pick a completely different, real video."
            )

        career_prompt = (
            f"You are a career counselor helping someone explore the '{career_name}' career in the {industry} industry. "
            f"Career Details: {description}. Required Skills: {skills_str}. "
            "Task: Provide a thoughtful 2-3 sentence recommendation about this career path, name one complementary related career, "
            f"and find a REAL YouTube video specifically about the '{career_name}' career — such as a day-in-the-life, "
            "how to become one, or a career overview by a practitioner or educator. "
            "IMPORTANT: The video MUST be directly about this specific career. "
            "DO NOT use joke videos, music videos, or general placeholder videos. "
            "The resourceUrl MUST be in the format https://www.youtube.com/embed/VIDEO_ID only. "
            "DO NOT use youtube.com/watch, youtube.com/results, or any other URL format."
            + exclusion_note
        )

        try:
            response = client.models.generate_content(
                model=MODEL,
                contents=career_prompt,
                config={
                    "response_mime_type": "application/json",
                    "response_schema": recommendation_schema
                }
            )
            result = json.loads(response.text)
        except Exception as e:
            last_error = str(e)
            print(f"Attempt {attempt}: Gemini call/parse failed: {last_error}")
            # On quota exhaustion, stop retrying immediately
            if "429" in last_error or "RESOURCE_EXHAUSTED" in last_error:
                print("Gemini quota exceeded — stopping retries.")
                break
            continue

        resource_url = result.get("resourceUrl", "")
        print(f"Attempt {attempt}: Got video URL: {resource_url}")

        # Check against blacklist only
        video_id = ""
        if "/embed/" in resource_url:
            video_id = resource_url.split("/embed/")[1].split("?")[0]
        
        if video_id and video_id in BLACKLISTED_IDS:
             print(f"Attempt {attempt}: Video ID {video_id} is blacklisted (joke/placeholder). Retrying...")
             invalid_ids.append(video_id)
             # If this was the last attempt, clear the resourceUrl
             if attempt == MAX_RETRIES:
                 result["resourceUrl"] = ""
             # Fall back to keep this result but continue loop to retry if possible
             if recommendation is None:
                 recommendation = result
             continue # Retry to get a better video

        recommendation = result
        break

    if recommendation is None:
        msg = "Unable to generate recommendation at this time."
        if last_error and ("429" in last_error or "RESOURCE_EXHAUSTED" in last_error):
            msg = "Daily AI quota exceeded. Showing standard career details instead."
        
        return {"recommendation": msg, "relatedCareer": "", "resourceUrl": ""}

    return recommendation


# ---------------------------------------------------------------------------
# AI integration notes (ai.gemini)
# ---------------------------------------------------------------------------
# - Loads `GEMINI_API_KEY` from `.env` and attempts to initialize the Google
#   GenAI client. If the client fails to initialize the functions raise a clear
#   exception so the API layer can return a 5xx with an explanatory message.
# - `format_user_responses_for_llm` converts quiz response objects into a
#   single-line summary that is safer for prompt engineering and reduces
#   chances of malformed LLM outputs.
# - `get_gemini_recommendations` and `get_career_recommendation` build a
#   schema-backed prompt so the model returns predictable JSON structures.
# - Important production considerations (not fully implemented):
#   * Implement caching for identical requests to reduce cost and latency.
#   * Add quota handling and graceful fallbacks when the LLM is unavailable.
#   * Validate and sanitize LLM outputs before returning them to clients.
# ---------------------------------------------------------------------------
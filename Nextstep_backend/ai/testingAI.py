'''
this first file is for testing the gemini api
'''
# from google import genai
# from pathlib import Path
# BASE_DIR = Path(__file__).resolve().parent.parent
# from dotenv import load_dotenv
# import os
# # Load environment variables from .env file
# load_dotenv(BASE_DIR / '.env')
# GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
# # CORS_ALLOW_CREDENTIALS = True
# # The client gets the API key from the environment variable `GEMINI_API_KEY`.
# client = genai.Client()

# # response = client.models.generate_content(
# #     model="gemini-2.5-flash", contents="Can you generate a json file"
# # )
# # print(response.text)


# # In your app's service or views.py
# import json

# def get_gemini_recommendations(user_history):
#     prompt_parts = [
#         {"text": "You are a professional recommendation engine. Your task is to recommend as many carrer based on the user's answers. Only output a JSON array of objects."},
#         {"text": f"User's answers: {user_history}"},
#         {"text": "Return result in the following format: [{'career': 'recommended_career', 'reason': 'Why you recommend it'},...] next line after each key value pair."}
#     ]
    
#     response = client.models.generate_content(
#         model="gemini-2.5-flash",
#         contents=prompt_parts,
#         config={
#             "response_mime_type": "application/json",
#             "response_schema": {
#                 "type": "array",
#                 "items": {
#                     "type": "object",
#                     "properties": {
#                         "career": {"type": "string"},
#                         "reason": {"type": "string"}
#                     }
#                 }
#             }
#         }
#     )
    
#     # Parse the structured JSON response
#     try:
#         recommendations = json.loads(response.text)
#         return recommendations
#     except json.JSONDecodeError:
#         print("Error decoding JSON response from Gemini.")
#         return []

# # Example usage in a view
# user_liked_books = {
#   "responses": [
#     {
#       "question": "Which of these activities sounds most interesting to you?",
#       "answer": "Helping people"
#     },
#     {
#       "question": "What kind of school projects excite you most?",
#       "answer": "Science fair builds"
#     },
#     {
#       "question": "How soon do you want to start earning while learning?",
#       "answer": "After finishing school"
#     },
#     {
#       "question": "Which subject at school do you enjoy most?",
#       "answer": "Art / Design"
#     },
#     {
#       "question": "Do you prefer structured guidance or self-directed learning?",
#       "answer": "Self-directed (online, projects)"
#     },
#     {
#       "question": "Do you prefer working indoors (office/lab) or outdoors (field/site)?",
#       "answer": "Indoors (office/lab)"
#     },
#     {
#       "question": "When facing a tough problem, you usually...",
#       "answer": "Ask for help immediately"
#     },
#     {
#       "question": "If you had $100 for a project, what would you spend it on?",
#       "answer": "A course/book for skills"
#     },
#     {
#       "question": "How do you feel about routine tasks vs. constantly changing work?",
#       "answer": "A balance of both is ideal"
#     },
#     {
#       "question": "What's more motivating?",
#       "answer": "Achieving a high grade"
#     },
#     {
#       "question": "What is your main goal as a student?",
#       "answer": "Get a job"
#     },
#     {
#       "question": "How much time can you commit weekly to learning/career activities?",
#       "answer": ">20 hours"
#     }
#   ]
# }
# recommendations = get_gemini_recommendations(user_liked_books)
# print(recommendations)

# #

"""This file make the output look better in cmd """
import json
import os
from pathlib import Path
from dotenv import load_dotenv
from google import genai
from typing import Dict, Any, List

# --- API KEY & CLIENT SETUP ---
# (Assuming the API key setup is correct and client is initialized)
# Determine the base directory for locating the .env file
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / '.env')
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

try:
    client = genai.Client()
except Exception:
    print("Error initializing Gemini client. Check GEMINI_API_KEY.")
    exit()

MODEL = "gemini-2.5-flash"

# --- DATA PROCESSING FUNCTION (IMPROVED) ---
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


# --- GEMINI API CALL FUNCTION (IMPROVED) ---
def get_gemini_recommendations(user_history: Dict[str, Any]) -> List[Dict[str, str]]:
    """
    Sends the user's quiz responses to the Gemini API to receive structured 
    career recommendations.
    """
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
        contents=career_prompt, # Pass the entire prompt as a single string
        config={
            "response_mime_type": "application/json",
            "response_schema": career_schema
        }
    )
    
    # 5. Parse the structured JSON response
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


# --- EXAMPLE USAGE ---

# Sample user quiz responses (kept from your original input)
user_quiz_responses = {
    "responses": [
        {"question": "Which of these activities sounds most interesting to you?", "answer": "Helping people"},
        {"question": "What kind of school projects excite you most?", "answer": "Science fair builds"},
        {"question": "How soon do you want to start earning while learning?", "answer": "After finishing school"},
        {"question": "Which subject at school do you enjoy most?", "answer": "Biology / Science"},
        {"question": "Do you prefer structured guidance or self-directed learning?", "answer": "A balance of both is ideal"},
        {"question": "Do you prefer working indoors (office/lab) or outdoors (field/site)?", "answer": "Indoors (office/lab)"},
        {"question": "When facing a tough problem, you usually...", "answer": "Ask for help immediately"},
        {"question": "If you had $100 for a project, what would you spend it on?", "answer": "A course/book for skills"},
        {"question": "How do you feel about routine tasks vs. constantly changing work?", "answer": "A balance of both is ideal"},
        {"question": "What's more motivating?", "answer": "Achieving a high grade"},
        {"question": "What is your main goal as a student?", "answer": "Get a job"},
        {"question": "How much time can you commit weekly to learning/career activities?", "answer": ">20 hours"}
    ]
}

# Get the recommendations
recommendations = get_gemini_recommendations(user_quiz_responses)

# Print the result with indentation (indent=4)
if recommendations:
    pretty_json = json.dumps(recommendations, indent=4)
    print("\n--- Career Recommendations (Formatted Output) ---")
    print(pretty_json)
else:
    print("Could not generate valid JSON recommendations.")
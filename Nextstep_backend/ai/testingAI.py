from google import genai
from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent.parent
from dotenv import load_dotenv
import os
# Load environment variables from .env file
load_dotenv(BASE_DIR / '.env')
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
CORS_ALLOW_CREDENTIALS = True
# The client gets the API key from the environment variable `GEMINI_API_KEY`.
client = genai.Client()

response = client.models.generate_content(
    model="gemini-2.5-flash", contents="Explain how AI works in a few words. Also say I love Nextstep."
)
print(response.text)

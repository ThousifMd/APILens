import os
from dotenv import load_dotenv

# Explicitly load the .env file using absolute path
load_dotenv(dotenv_path="/Users/thousifudayagiri/Desktop/MainWrapper/.env")

print("OPENAI API KEY:", os.getenv("OPENAI_API_KEY"))
print("GEMINI API KEY:", os.getenv("GEMINI_API_KEY"))
print("ANTHROPIC API KEY:", os.getenv("ANTHROPIC_API_KEY"))

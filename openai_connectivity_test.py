import os
import openai

api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    print("OPENAI_API_KEY not set in environment.")
    exit(1)

openai.api_key = api_key

try:
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": "Hello!"}]
    )
    print("OpenAI API call succeeded. Response snippet:")
    print(response.choices[0].message.content[:100])
except Exception as e:
    print(f"OpenAI API call failed: {e}") 
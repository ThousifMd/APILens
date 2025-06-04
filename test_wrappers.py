import os
from apilens import OpenAIWrapper, GeminiWrapper, ClaudeWrapper, APILoggerREST

# Set up logger
logger = APILoggerREST(api_url=os.getenv("POSTGRES_DB_URL"))

def test_openai():
    print("\n--- OpenAI ---")
    client = OpenAIWrapper(model="gpt-4", logger=logger)
    response = client.chat_completion(
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Who is the captain of RCB?"}
        ]
    )
    print("OpenAI Response:", response["choices"][0]["message"]["content"])
    print("OpenAI Usage:", response["usage"])
    print("OpenAI Cost:", response["cost"])

def test_gemini():
    print("\n--- Gemini ---")
    client = GeminiWrapper(model="gemini-2.5-pro-preview-05-06", logger=logger)
    response = client.chat_completion(
        messages=[
            {"role": "user", "content": "Who is the captain of RCB?"}
        ]
    )
    print("Gemini Response:", response["choices"][0]["message"]["content"])
    print("Gemini Usage:", response["usage"])
    print("Gemini Cost:", response["cost"])

def test_claude():
    print("\n--- Claude ---")
    client = ClaudeWrapper(model="claude-3-haiku-20240307", logger=logger)
    # Claude expects only user/assistant messages, not system
    response = client.chat_completion(
        messages=[
            {"role": "user", "content": "Who is the captain of RCB?"}
        ]
    )
    print("Claude Response:", response["choices"][0]["message"]["content"])
    print("Claude Usage:", response["usage"])
    print("Claude Cost:", response["cost"])

if __name__ == "__main__":
    test_openai()
    test_gemini()
    test_claude() 
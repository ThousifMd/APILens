from apilens import OpenAIWrapper, GeminiWrapper

def main():
    try:
        # Initialize the OpenAI client
        openai_client = OpenAIWrapper(model="gpt-3.5-turbo")
        
        # Create a simple message for OpenAI
        openai_messages = [
            {"role": "user", "content": "Say hello and tell me what time it is."}
        ]
        
        # Make the OpenAI API call
        print("Making OpenAI API call...")
        openai_response = openai_client.chat_completion(openai_messages)
        
        # Print the OpenAI response
        print("\nOpenAI Response received:")
        print(openai_response.choices[0].message.content)
        
        # Initialize the Gemini client
        gemini_client = GeminiWrapper(model="gemini-1.5-pro")
        
        # Create a simple message for Gemini
        gemini_messages = [
            {"role": "user", "content": "Say hello and tell me what time it is."}
        ]
        
        # Make the Gemini API call
        print("\nMaking Gemini API call...")
        gemini_response = gemini_client.chat_completion(gemini_messages)
        
        # Print the Gemini response
        print("\nGemini Response received:")
        print(gemini_response["choices"][0]["message"]["content"])
        
    except Exception as e:
        print("\nError occurred:", str(e))

if __name__ == "__main__":
    main()

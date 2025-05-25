from dotenv import load_dotenv
load_dotenv()
from apilens import OpenAIWrapper, GeminiWrapper, AnthropicWrapper
import csv
from datetime import datetime
import os



# Debug prints
print("Current working directory:", os.getcwd())
print("ANTHROPIC_API_KEY exists:", bool(os.getenv("ANTHROPIC_API_KEY")))
print("ANTHROPIC_API_KEY value:", os.getenv("ANTHROPIC_API_KEY")[:5] + "..." if os.getenv("ANTHROPIC_API_KEY") else None)
print("POSTGRES_DB_URL exists:", bool(os.getenv("POSTGRES_DB_URL")))
print("POSTGRES_DB_URL value:", os.getenv("POSTGRES_DB_URL"))

def clean_text(text):
    """Clean text for CSV by replacing newlines with spaces and removing extra whitespace"""
    if isinstance(text, str):
        return ' '.join(text.replace('\n', ' ').split())
    return text

def write_to_csv(model, provider, input_message, response, prompt_tokens, completion_tokens, cost, status, error=None):
    # Debug print to check CSV file path
    csv_file = 'results/test_results.csv'
    print("CSV File Path:", csv_file)
    # Create results directory if it doesn't exist
    if not os.path.exists('results'):
        os.makedirs('results')
    # Define CSV file path
    # csv_file = 'results/test_results.csv'  # Commented out as it's already defined above
    # Check if file exists to determine if we need to write headers
    file_exists = os.path.isfile(csv_file)
    with open(csv_file, 'a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f, quoting=csv.QUOTE_ALL)
        # Write headers if file is new
        if not file_exists:
            writer.writerow([
                'Timestamp',
                'Model',
                'Provider',
                'Input Message',
                'Response',
                'Prompt Tokens',
                'Completion Tokens',
                'Total Tokens',
                'Cost ($)',
                'Status',
                'Error'
            ])
        # Calculate total tokens
        total_tokens = prompt_tokens + completion_tokens
        # Clean text fields
        input_message = clean_text(input_message)
        response = clean_text(response)
        error = clean_text(error) if error else ''
        # Write the data
        writer.writerow([
            datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            model,
            provider,
            input_message,
            response,
            prompt_tokens,
            completion_tokens,
            total_tokens,
            f"{cost:.6f}",
            status,
            error
        ])

def main():
    try:
        # OpenAI API call
        print("Initializing OpenAIWrapper...")
        openai_client = OpenAIWrapper(model="gpt-4")
        print("OpenAIWrapper initialized.")
        openai_messages = [{"role": "user", "content": "Print the first 20 prime numbers."}]
        print("Making OpenAI API call...")
        openai_response = openai_client.chat_completion(openai_messages)
        print("OpenAI Response:", openai_response)
        print("Type of OpenAI Response:", type(openai_response))
        usage = openai_response.get("usage", {})
        prompt_tokens = usage.get("prompt_tokens", 0)
        completion_tokens = usage.get("completion_tokens", 0)
        cost = openai_response.get("cost", 0.0)
        print("OpenAI Usage:", usage)
        print("OpenAI Prompt Tokens:", prompt_tokens)
        print("OpenAI Completion Tokens:", completion_tokens)
        print("OpenAI Cost:", cost)
        print("OpenAI call completed successfully.")
        write_to_csv(
            model="gpt-4",
            provider="OpenAI",
            input_message=openai_messages[0]["content"],
            response=openai_response.get("choices", [{}])[0].get("message", {}).get("content", ""),
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            cost=cost,
            status="success"
        )

        # Gemini API call
        print("Initializing GeminiWrapper...")
        gemini_client = GeminiWrapper(model="gemini-2.5-pro-preview-05-06")
        print("GeminiWrapper initialized.")
        gemini_messages = [{"role": "user", "content": "Print the first 20 prime numbers."}]
        print("\nMaking Gemini API call...")
        gemini_response = gemini_client.chat_completion(gemini_messages)
        print("Gemini Response:", gemini_response)
        print("Type of Gemini Response:", type(gemini_response))
        usage = gemini_response.get("usage", {})
        prompt_tokens = usage.get("prompt_tokens", 0)
        completion_tokens = usage.get("completion_tokens", 0)
        cost = gemini_response.get("cost", 0.0)
        print("Gemini Usage:", usage)
        print("Gemini Prompt Tokens:", prompt_tokens)
        print("Gemini Completion Tokens:", completion_tokens)
        print("Gemini Cost:", cost)
        write_to_csv(
            model="gemini-2.5-pro-preview-05-06",
            provider="Gemini",
            input_message=gemini_messages[0]["content"],
            response=gemini_response["choices"][0]["message"]["content"],
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            cost=cost,
            status="success"
        )

        # Anthropic API call
        print("Initializing AnthropicWrapper...")
        anthropic_client = AnthropicWrapper(model="claude-3-haiku-20240307")
        print("AnthropicWrapper initialized.")
        anthropic_messages = [
            {"role": "system", "content": "You are a helpful AI assistant that specializes in explaining complex topics in simple terms."},
            {"role": "user", "content": "Print the first 20 prime numbers."}
        ]
        print("\nMaking Anthropic (Claude) API call...")
        anthropic_response = anthropic_client.chat_completion(
            messages=anthropic_messages,
            max_tokens=1000,
            temperature=0.7
        )
        print("Anthropic Response:", anthropic_response)
        print("Type of Anthropic Response:", type(anthropic_response))
        usage = anthropic_response.get("usage", {})
        prompt_tokens = usage.get("prompt_tokens", 0)
        completion_tokens = usage.get("completion_tokens", 0)
        cost = anthropic_response.get("cost", 0.0)
        print("Anthropic Usage:", usage)
        print("Anthropic Prompt Tokens:", prompt_tokens)
        print("Anthropic Completion Tokens:", completion_tokens)
        print("Anthropic Cost:", cost)
        write_to_csv(
            model="claude-3-haiku-20240307",
            provider="Anthropic",
            input_message=anthropic_messages[1]["content"],
            response=anthropic_response.get("choices", [{}])[0].get("message", {}).get("content", ""),
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            cost=cost,
            status="success"
        )
        
    except Exception as e:
        error_message = str(e)
        print("\nError occurred:", error_message)
        # Write error to CSV
        write_to_csv(
            model="unknown",
            provider="unknown",
            input_message="Test failed",
            response="",
            prompt_tokens=0,
            completion_tokens=0,
            cost=0.0,
            status="failed",
            error=error_message
        )

if __name__ == "__main__":
    main()

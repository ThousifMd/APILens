from dotenv import load_dotenv
load_dotenv()
from apilens import AnthropicWrapper
import pytest
from unittest.mock import patch

def test_anthropic():
    try:
        # Initialize the wrapper with Claude 3 Haiku
        client = AnthropicWrapper(model="claude-3-haiku-20240307")
        
        # Test with system message and user message
        messages = [
            {"role": "system", "content": "You are a helpful AI assistant that specializes in explaining complex topics in simple terms."},
            {"role": "user", "content": "Explain quantum computing in simple terms."}
        ]
        
        print("Making Anthropic API call...")
        response = client.chat_completion(
            messages=messages,
            max_tokens=1000,
            temperature=0.7
        )
        
        # Print the response
        print("\nResponse:")
        print(response["choices"][0]["message"]["content"])
        
        # Print usage and cost information
        usage = response.get("usage", {})
        cost = response.get("cost", 0.0)
        print(f"\nUsage:")
        print(f"Prompt tokens: {usage.get('prompt_tokens', 0)}")
        print(f"Completion tokens: {usage.get('completion_tokens', 0)}")
        print(f"Total cost: ${cost:.6f}")
        
    except Exception as e:
        print(f"\nError occurred: {str(e)}")

# 1. Unsupported model
def test_unsupported_model():
    with pytest.raises(ValueError):
        AnthropicWrapper(model="not-a-real-model")

# 2. Missing API key
def test_missing_api_key(monkeypatch):
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    from apilens import AnthropicWrapper
    client = AnthropicWrapper(model="claude-3-haiku-20240307")
    with patch.object(client.client, 'messages', create=True) as mock_messages:
        mock_messages.create.side_effect = Exception("API key missing")
        with pytest.raises(Exception) as excinfo:
            client.chat_completion([{"role": "user", "content": "Test"}])
        assert "API key missing" in str(excinfo.value)

# 3. API error/timeout (mocked)
def test_api_error_handling():
    client = AnthropicWrapper(model="claude-3-haiku-20240307")
    with patch.object(client.client, 'messages', create=True) as mock_messages:
        mock_messages.create.side_effect = Exception("API error!")
        with pytest.raises(Exception) as excinfo:
            client.chat_completion([{"role": "user", "content": "Test"}])
        assert "API error!" in str(excinfo.value)

# 4. Malformed input
def test_malformed_input():
    client = AnthropicWrapper(model="claude-3-haiku-20240307")
    # Missing 'role'
    messages = [{"content": "Hello!"}]
    with pytest.raises(ValueError, match="missing 'role'"):
        client.chat_completion(messages)
    # Missing 'content'
    messages = [{"role": "user"}]
    with pytest.raises(ValueError, match="missing or empty 'content'"):
        client.chat_completion(messages)
    # Empty 'content'
    messages = [{"role": "user", "content": ""}]
    with pytest.raises(ValueError, match="missing or empty 'content'"):
        client.chat_completion(messages)

# 5. Cost calculation
def test_cost_calculation():
    client = AnthropicWrapper(model="claude-3-haiku-20240307")
    messages = [{"role": "user", "content": "Hello!"}]
    response = client.chat_completion(messages)
    assert "cost" in response
    assert isinstance(response["cost"], float)

# 6. Large/empty prompt
def test_empty_prompt():
    client = AnthropicWrapper(model="claude-3-haiku-20240307")
    messages = [{"role": "user", "content": ""}]
    with pytest.raises(ValueError, match="missing or empty 'content'"):
        client.chat_completion(messages)

def test_large_prompt():
    client = AnthropicWrapper(model="claude-3-haiku-20240307")
    large_text = "Hello! " * 1000
    messages = [{"role": "user", "content": large_text}]
    response = client.chat_completion(messages)
    assert response is not None
    assert "choices" in response

if __name__ == "__main__":
    test_anthropic() 
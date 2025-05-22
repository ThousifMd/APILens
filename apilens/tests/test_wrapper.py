import os
import pytest
from unittest.mock import patch
from apilens.openai_wrapper import OpenAIWrapper

def test_wrapper_creation():
    # Set a test API key in the environment
    os.environ["OPENAI_API_KEY"] = "test-key"
    wrapper = OpenAIWrapper(model="gpt-3.5-turbo")
    assert wrapper is not None

# 1. Unsupported model
def test_unsupported_model():
    os.environ["OPENAI_API_KEY"] = "test-key"
    with pytest.raises(ValueError):
        OpenAIWrapper(model="not-a-real-model")

# 2. Missing API key
def test_missing_api_key(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    wrapper = OpenAIWrapper(model="gpt-3.5-turbo")
    with patch.object(wrapper.client.chat.completions, 'create', side_effect=Exception("API key missing")):
        with pytest.raises(Exception) as excinfo:
            wrapper.chat_completion([{"role": "user", "content": "Test"}])
        assert "API key missing" in str(excinfo.value)

# 3. API error/timeout (mocked)
def test_api_error_handling():
    os.environ["OPENAI_API_KEY"] = "test-key"
    wrapper = OpenAIWrapper(model="gpt-3.5-turbo")
    with patch.object(wrapper.client.chat.completions, 'create', side_effect=Exception("API error!")):
        with pytest.raises(Exception) as excinfo:
            wrapper.chat_completion([{"role": "user", "content": "Test"}])
        assert "API error!" in str(excinfo.value)

# 4. Malformed input
def test_malformed_input():
    os.environ["OPENAI_API_KEY"] = "test-key"
    wrapper = OpenAIWrapper(model="gpt-3.5-turbo")
    # Missing 'role'
    messages = [{"content": "Hello!"}]
    with pytest.raises(ValueError, match="missing 'role'"):
        wrapper.chat_completion(messages)
    # Missing 'content'
    messages = [{"role": "user"}]
    with pytest.raises(ValueError, match="missing or empty 'content'"):
        wrapper.chat_completion(messages)
    # Empty 'content'
    messages = [{"role": "user", "content": ""}]
    with pytest.raises(ValueError, match="missing or empty 'content'"):
        wrapper.chat_completion(messages)

# 5. Cost calculation
def test_cost_calculation():
    os.environ["OPENAI_API_KEY"] = "test-key"
    wrapper = OpenAIWrapper(model="gpt-3.5-turbo")
    messages = [{"role": "user", "content": "Hello!"}]
    response = wrapper.chat_completion(messages)
    assert "cost" in response
    assert isinstance(response["cost"], float)

# 6. Large/empty prompt
def test_empty_prompt():
    os.environ["OPENAI_API_KEY"] = "test-key"
    wrapper = OpenAIWrapper(model="gpt-3.5-turbo")
    messages = [{"role": "user", "content": ""}]
    with pytest.raises(ValueError, match="missing or empty 'content'"):
        wrapper.chat_completion(messages)

def test_large_prompt():
    os.environ["OPENAI_API_KEY"] = "test-key"
    wrapper = OpenAIWrapper(model="gpt-3.5-turbo")
    large_text = "Hello! " * 1000
    messages = [{"role": "user", "content": large_text}]
    response = wrapper.chat_completion(messages)
    assert response is not None
    assert "choices" in response

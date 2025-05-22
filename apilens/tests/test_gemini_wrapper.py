import os
import pytest
from unittest.mock import patch, MagicMock
import importlib
from apilens.gemini_wrapper import GeminiWrapper

def test_gemini_wrapper_creation():
    # Set a test API key in the environment
    os.environ["GEMINI_API_KEY"] = "test-key"
    wrapper = GeminiWrapper(model="gemini-2.5-pro-preview-05-06")
    assert wrapper is not None

def test_gemini_chat_completion():
    # Set a test API key in the environment
    os.environ["GEMINI_API_KEY"] = "test-key"
    wrapper = GeminiWrapper(model="gemini-2.5-pro-preview-05-06")
    messages = [{"role": "user", "content": "Hello, Gemini!"}]
    response = wrapper.chat_completion(messages)
    assert response is not None
    assert "choices" in response

# 1. Unsupported model
def test_unsupported_model():
    os.environ["GEMINI_API_KEY"] = "test-key"
    with pytest.raises(ValueError):
        GeminiWrapper(model="not-a-real-model")

# 2. Missing API key
def test_missing_api_key(monkeypatch):
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    import apilens.gemini_wrapper as gemini_wrapper_mod
    importlib.reload(gemini_wrapper_mod)
    wrapper = gemini_wrapper_mod.GeminiWrapper(model="gemini-2.5-pro-preview-05-06")
    with patch.object(wrapper.client, 'generate_content', side_effect=Exception("API key missing")):
        with pytest.raises(Exception) as excinfo:
            wrapper.chat_completion([{"role": "user", "content": "Test"}])
        assert "API key missing" in str(excinfo.value)

# 3. API error/timeout (mocked)
def test_api_error_handling():
    os.environ["GEMINI_API_KEY"] = "test-key"
    wrapper = GeminiWrapper(model="gemini-2.5-pro-preview-05-06")
    with patch.object(wrapper.client, 'generate_content', side_effect=Exception("API error!")):
        with pytest.raises(Exception) as excinfo:
            wrapper.chat_completion([{"role": "user", "content": "Test"}])
        assert "API error!" in str(excinfo.value)

# 4. Malformed input
def test_malformed_input():
    os.environ["GEMINI_API_KEY"] = "test-key"
    wrapper = GeminiWrapper(model="gemini-2.5-pro-preview-05-06")
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
    os.environ["GEMINI_API_KEY"] = "test-key"
    wrapper = GeminiWrapper(model="gemini-2.5-pro-preview-05-06")
    messages = [{"role": "user", "content": "Hello!"}]
    response = wrapper.chat_completion(messages)
    assert "cost" in response
    assert isinstance(response["cost"], float)

# 6. Large/empty prompt
def test_empty_prompt():
    os.environ["GEMINI_API_KEY"] = "test-key"
    wrapper = GeminiWrapper(model="gemini-2.5-pro-preview-05-06")
    messages = [{"role": "user", "content": ""}]
    with pytest.raises(ValueError, match="missing or empty 'content'"):
        wrapper.chat_completion(messages)

def test_large_prompt():
    os.environ["GEMINI_API_KEY"] = "test-key"
    wrapper = GeminiWrapper(model="gemini-2.5-pro-preview-05-06")
    large_text = "Hello! " * 1000
    messages = [{"role": "user", "content": large_text}]
    response = wrapper.chat_completion(messages)
    assert response is not None
    assert "choices" in response 
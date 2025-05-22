# New Features and Changes Documentation

## Overview
This document outlines the new features and changes made to the API Lens library, including async support, streaming, improved error handling, and configurable retry strategies.

## Table of Contents
1. [Async Support](#async-support)
2. [Streaming Support](#streaming-support)
3. [Error Handling](#error-handling)
4. [Retry Strategy](#retry-strategy)
5. [Response Format](#response-format)
6. [Testing](#testing)

## Async Support

### Usage
```python
from apilens import OpenAIWrapper, AnthropicWrapper

# OpenAI Async
async def main():
    wrapper = OpenAIWrapper(model="gpt-4")
    response = await wrapper.async_chat_completion(
        messages=[{"role": "user", "content": "Hello!"}]
    )
    print(response["choices"][0]["message"]["content"])

# Anthropic Async
async def main():
    wrapper = AnthropicWrapper(model="claude-3-opus-20240229")
    response = await wrapper.async_chat_completion(
        messages=[{"role": "user", "content": "Hello!"}]
    )
    print(response["choices"][0]["message"]["content"])
```

### Implementation Details
- Uses `AsyncOpenAI` and `AsyncAnthropic` clients
- Maintains separate async and sync clients
- Supports all parameters from sync version
- Includes async retry mechanism

## Streaming Support

### Usage
```python
from apilens import OpenAIWrapper

wrapper = OpenAIWrapper(model="gpt-4")
for chunk in wrapper.chat_completion_stream(
    messages=[{"role": "user", "content": "Hello!"}]
):
    print(chunk["choices"][0]["message"]["content"])
```

### Implementation Details
- Yields response chunks as they arrive
- Maintains consistent response format
- Handles streaming errors gracefully
- Logs final usage after stream completion

## Error Handling

### Error Types
```python
from apilens import (
    APILensError,
    RateLimitError,
    AuthError,
    BadRequestError,
    ProviderError
)
```

### Usage
```python
try:
    response = wrapper.chat_completion(messages=[{"role": "user", "content": "Hello!"}])
except RateLimitError:
    print("Rate limit exceeded, try again later")
except AuthError:
    print("Authentication failed, check your API key")
except BadRequestError:
    print("Invalid request, check your parameters")
except ProviderError as e:
    print(f"Provider error: {e}")
```

## Retry Strategy

### Configuration
```python
wrapper = OpenAIWrapper(
    model="gpt-4",
    max_retries=5,        # Number of retry attempts
    backoff_base=2.0,     # Exponential backoff base
    timeout=60            # Request timeout in seconds
)
```

### Default Values
- `max_retries`: 3
- `backoff_base`: 1.0
- `timeout`: 30 seconds

### Retry Behavior
- Exponential backoff: wait_time = (backoff_base ^ attempt) * 1 second
- Retries on rate limits and network errors
- No retry on authentication or bad request errors

## Response Format

### Standard Response Structure
```python
{
    "choices": [{
        "message": {
            "content": "Response text"
        }
    }],
    "usage": {
        "prompt_tokens": 10,
        "completion_tokens": 20
    },
    "cost": 0.0015  # Calculated cost in USD
}
```

### Type Definition
```python
from apilens import LLMResponse

# Type hints
response: LLMResponse = wrapper.chat_completion(messages=[...])
```

## Testing

### Running Tests
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=apilens

# Run specific test file
pytest tests/test_new_features.py

# Run async tests
pytest -m asyncio
```

### Test Categories
1. **Async Tests**
   - Tests async chat completion
   - Verifies response format
   - Checks error handling

2. **Streaming Tests**
   - Tests chunk delivery
   - Verifies stream format
   - Checks stream completion

3. **Error Handling Tests**
   - Tests rate limit errors
   - Tests authentication errors
   - Tests bad request errors

4. **Retry Tests**
   - Tests successful retries
   - Tests retry exhaustion
   - Tests custom configurations

5. **Response Format Tests**
   - Tests response structure
   - Verifies field types
   - Checks cost calculation

### Mock Usage
```python
from unittest.mock import Mock, patch, AsyncMock

# Mock response
mock_response = Mock()
mock_response.choices = [Mock(message=Mock(content="Hello!"))]
mock_response.usage = Mock(prompt_tokens=10, completion_tokens=20)

# Patch API call
with patch.object(wrapper.client.chat.completions, 'create',
                 return_value=mock_response):
    response = wrapper.chat_completion(messages=[...])
```

## Migration Guide

### From Previous Version
1. Update imports to include new types:
   ```python
   from apilens import (
       OpenAIWrapper,
       AnthropicWrapper,
       LLMResponse,
       APILensError
   )
   ```

2. Update error handling:
   ```python
   try:
       response = wrapper.chat_completion(messages=[...])
   except APILensError as e:
       # Handle specific error types
   ```

3. Add async support if needed:
   ```python
   async def process():
       response = await wrapper.async_chat_completion(messages=[...])
   ```

4. Configure retry strategy:
   ```python
   wrapper = OpenAIWrapper(
       max_retries=5,
       backoff_base=2.0,
       timeout=60
   )
   ```

## Best Practices

1. **Error Handling**
   - Always catch specific error types
   - Handle rate limits appropriately
   - Log authentication errors

2. **Async Usage**
   - Use async for concurrent requests
   - Handle async errors properly
   - Use appropriate async context managers

3. **Streaming**
   - Process chunks as they arrive
   - Handle stream interruptions
   - Monitor stream completion

4. **Retry Configuration**
   - Adjust retries based on use case
   - Consider rate limits when setting backoff
   - Set appropriate timeouts

5. **Response Processing**
   - Use type hints for better IDE support
   - Validate response structure
   - Handle missing fields gracefully 
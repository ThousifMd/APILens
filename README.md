# API Lens

A unified wrapper for multiple LLM providers with standardized logging, cost tracking, and error handling.

## Features

- **Multiple Provider Support**
  - OpenAI (GPT-3.5, GPT-4)
  - Anthropic (Claude)
  - More providers coming soon!

- **Unified Interface**
  - Consistent API across providers
  - Standardized response format
  - Type-safe responses

- **Advanced Features**
  - Async support for concurrent requests
  - Streaming responses
  - Configurable retry strategies
  - Comprehensive error handling

- **Usage Tracking**
  - Token usage logging
  - Cost calculation
  - Multi-tenant support
  - User tracking

## Installation

```bash
pip install apilens
```

## Quick Start

```python
from apilens import OpenAIWrapper, AnthropicWrapper

# OpenAI
openai = OpenAIWrapper(model="gpt-4")
response = openai.chat_completion(
    messages=[{"role": "user", "content": "Hello!"}]
)

# Anthropic
anthropic = AnthropicWrapper(model="claude-3-opus-20240229")
response = anthropic.chat_completion(
    messages=[{"role": "user", "content": "Hello!"}]
)

# Async Usage
async def main():
    response = await openai.async_chat_completion(
        messages=[{"role": "user", "content": "Hello!"}]
    )

# Streaming
for chunk in openai.chat_completion_stream(
    messages=[{"role": "user", "content": "Hello!"}]
):
    print(chunk["choices"][0]["message"]["content"])
```

## Configuration

```python
wrapper = OpenAIWrapper(
    model="gpt-4",
    max_retries=5,        # Number of retry attempts
    backoff_base=2.0,     # Exponential backoff base
    timeout=60,           # Request timeout in seconds
    user_id="user123",    # Optional user tracking
    tenant_id="tenant1"   # Optional tenant tracking
)
```

## Error Handling

```python
from apilens import RateLimitError, AuthError, BadRequestError

try:
    response = wrapper.chat_completion(messages=[...])
except RateLimitError:
    print("Rate limit exceeded, try again later")
except AuthError:
    print("Authentication failed, check your API key")
except BadRequestError:
    print("Invalid request, check your parameters")
```

## Documentation

For detailed documentation, see:
- [New Features Guide](docs/new_features.md)
- [API Reference](docs/api_reference.md)
- [Migration Guide](docs/migration.md)

## Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=apilens

# Run specific test file
pytest tests/test_new_features.py
```

## Contributing

1. Fork the repository
2. Create your feature branch
3. Add tests for your changes
4. Ensure all tests pass
5. Submit a pull request

## License

MIT License - see LICENSE file for details

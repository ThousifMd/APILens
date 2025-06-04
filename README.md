# APILens

A unified wrapper for OpenAI, Anthropic Claude, and Google Gemini APIs with automatic logging to PostgreSQL database.

## Features

- **Unified Interface**: Use the same interface for all three major LLM providers
- **Automatic Logging**: All API calls are automatically logged to your PostgreSQL database
- **Cost Tracking**: Track token usage and costs for each API call
- **Timezone Support**: Logs include both IST and CST timestamps
- **Error Handling**: Comprehensive error handling and logging

## Installation

```bash
pip install apilens_test1
```

## Configuration

Set the following environment variables:

```bash
# API Keys
export OPENAI_API_KEY="sk-..."           # Your OpenAI API key
export ANTHROPIC_API_KEY="sk-ant-..."    # Your Anthropic API key
export GEMINI_API_KEY="..."              # Your Gemini API key

# Database URL (PostgreSQL)
export POSTGRES_DB_URL="postgresql://user:password@host:port/dbname?sslmode=require"
```

## Quick Start

```python
from apilens import OpenAIWrapper, GeminiWrapper, ClaudeWrapper, APILoggerREST

# Initialize logger (optional)
logger = APILoggerREST(api_url="your_postgres_db_url")

# OpenAI Example
openai_client = OpenAIWrapper(model="gpt-4", logger=logger)
response = openai_client.chat_completion(
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "What is the capital of France?"}
    ]
)
print(response["choices"][0]["message"]["content"])

# Gemini Example
gemini_client = GeminiWrapper(model="gemini-2.5-pro-preview-05-06", logger=logger)
response = gemini_client.chat_completion(
    messages=[
        {"role": "user", "content": "What is the capital of France?"}
    ]
)
print(response["choices"][0]["message"]["content"])

# Claude Example
claude_client = ClaudeWrapper(model="claude-3-haiku-20240307", logger=logger)
response = claude_client.chat_completion(
    messages=[
        {"role": "user", "content": "What is the capital of France?"}
    ]
)
print(response["choices"][0]["message"]["content"])
```

## Database Schema

The package automatically creates a table called `api_logs` with the following schema:

```sql
CREATE TABLE api_logs (
    id SERIAL PRIMARY KEY,
    created_at_ist TIMESTAMP WITH TIME ZONE DEFAULT (CURRENT_TIMESTAMP AT TIME ZONE 'Asia/Kolkata'),
    created_at_cst TIMESTAMP WITH TIME ZONE DEFAULT (CURRENT_TIMESTAMP AT TIME ZONE 'America/Chicago'),
    provider VARCHAR(50),
    model VARCHAR(100),
    prompt_tokens INTEGER,
    completion_tokens INTEGER,
    cost DECIMAL(10, 6),
    status VARCHAR(20),
    error_message TEXT,
    user_id VARCHAR(100),
    tenant_id VARCHAR(100)
);
```

## Supported Models

### OpenAI
- gpt-4
- gpt-4-turbo
- gpt-3.5-turbo

### Anthropic Claude
- claude-3-opus-20240229
- claude-3-sonnet-20240229
- claude-3-haiku-20240307

### Google Gemini
- gemini-pro
- gemini-pro-vision
- gemini-2.5-pro-preview-05-06

## Response Format

All wrappers return responses in a unified format:

```python
{
    "choices": [{
        "message": {
            "content": "The response text",
            "role": "assistant"
        }
    }],
    "usage": {
        "prompt_tokens": 10,
        "completion_tokens": 20,
        "total_tokens": 30
    },
    "cost": 0.0005
}
```

## Error Handling

The package includes comprehensive error handling:
- Invalid API keys
- Network errors
- Rate limiting
- Invalid model names
- Database connection issues

All errors are logged to the database with appropriate status and error messages.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

MIT License

## Support

For support, please open an issue in the GitHub repository.

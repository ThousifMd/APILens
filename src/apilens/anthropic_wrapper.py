import os
import logging
import anthropic
from .rest_logger import APILoggerREST

logger = logging.getLogger(__name__)

class ClaudeWrapper:
    def __init__(self, model="claude-3-opus-20240229", logger=None):
        self.model_name = model
        self.logger = logger or APILoggerREST()
        
        # Initialize Anthropic client
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY environment variable is not set")
        
        self.client = anthropic.Anthropic(api_key=api_key)

    def chat_completion(self, messages, **kwargs):
        try:
            # Convert messages to Claude format
            # Claude uses a different format than OpenAI
            system_message = None
            claude_messages = []
            
            for msg in messages:
                role = msg.get("role", "")
                content = msg.get("content", "")
                
                if role == "system":
                    system_message = content
                elif role == "user":
                    claude_messages.append({"role": "user", "content": content})
                elif role == "assistant":
                    claude_messages.append({"role": "assistant", "content": content})
            
            # Make the API call
            api_args = {
                "model": self.model_name,
                "messages": claude_messages,
                "max_tokens": kwargs.get("max_tokens", 4096),
                "temperature": kwargs.get("temperature", 0.7)
            }
            if system_message is not None:
                api_args["system"] = system_message

            response = self.client.messages.create(**api_args)
            
            # Get token usage from response
            prompt_tokens = response.usage.input_tokens
            completion_tokens = response.usage.output_tokens
            
            # Calculate cost based on Claude's pricing (as of 2024)
            # Claude 3 Opus: $15/million input tokens, $75/million output tokens
            # Claude 3 Sonnet: $3/million input tokens, $15/million output tokens
            # Claude 3 Haiku: $0.25/million input tokens, $1.25/million output tokens
            pricing = {
                "claude-3-opus-20240229": {"input": 15, "output": 75},
                "claude-3-sonnet-20240229": {"input": 3, "output": 15},
                "claude-3-haiku-20240307": {"input": 0.25, "output": 1.25}
            }
            
            model_pricing = pricing.get(self.model_name, pricing["claude-3-sonnet-20240229"])
            input_cost = (prompt_tokens / 1_000_000) * model_pricing["input"]
            output_cost = (completion_tokens / 1_000_000) * model_pricing["output"]
            total_cost = input_cost + output_cost
            
            # Log the API call
            if self.logger:
                self.logger.log_call(
                    provider="anthropic",
                    model=self.model_name,
                    prompt_tokens=prompt_tokens,
                    completion_tokens=completion_tokens,
                    cost=total_cost,
                    status="success",
                    error_message=None,
                    user_id=kwargs.get("user_id"),
                    tenant_id=kwargs.get("tenant_id")
                )
            
            # Return in a format similar to OpenAI's response
            return {
                "choices": [{
                    "message": {
                        "content": response.content[0].text,
                        "role": "assistant"
                    }
                }],
                "usage": {
                    "prompt_tokens": prompt_tokens,
                    "completion_tokens": completion_tokens,
                    "total_tokens": prompt_tokens + completion_tokens
                },
                "cost": total_cost
            }
            
        except Exception as e:
            logger.error(f"Error in Claude API call: {str(e)}")
            
            # Log the error
            if self.logger:
                self.logger.log_call(
                    provider="anthropic",
                    model=self.model_name,
                    prompt_tokens=0,
                    completion_tokens=0,
                    cost=0,
                    status="error",
                    error_message=str(e),
                    user_id=kwargs.get("user_id"),
                    tenant_id=kwargs.get("tenant_id")
                )
            
            raise 
import os
import logging
import openai
from .rest_logger import APILoggerREST
from .types import LLMResponse, APILensError, RateLimitError, AuthError, BadRequestError

logger = logging.getLogger(__name__)

class OpenAIWrapper:
    def __init__(self, model="gpt-4", logger=None):
        self.model_name = model
        self.logger = logger or APILoggerREST()
        
        # Initialize OpenAI client
        self.client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
        # Model pricing (cost per 1K tokens)
        self.pricing = {
            "gpt-4": {"input": 0.03, "output": 0.06},
            "gpt-4-turbo-preview": {"input": 0.01, "output": 0.03},
            "gpt-3.5-turbo": {"input": 0.0015, "output": 0.002}
        }
        
        if model not in self.pricing:
            logger.warning(f"Pricing not configured for model {model}. Using default pricing.")
            self.pricing[model] = {"input": 0.01, "output": 0.02}  # Default pricing

    def chat_completion(self, messages, temperature=0.7, max_tokens=None):
        try:
            # Make API call
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens
            )
            
            # Calculate cost
            prompt_tokens = response.usage.prompt_tokens
            completion_tokens = response.usage.completion_tokens
            total_cost = (
                (prompt_tokens / 1000 * self.pricing[self.model_name]["input"]) +
                (completion_tokens / 1000 * self.pricing[self.model_name]["output"])
            )
            
            # Log the API call
            self.logger.log_call(
                provider="openai",
                model=self.model_name,
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                cost=total_cost,
                status="success",
                error_message=None
            )
            
            return {
                "choices": [{"message": {"content": response.choices[0].message.content}}],
                "usage": {
                    "prompt_tokens": prompt_tokens,
                    "completion_tokens": completion_tokens,
                    "total_tokens": response.usage.total_tokens
                },
                "cost": total_cost
            }
            
        except openai.RateLimitError as e:
            logger.error(f"Rate limit exceeded: {str(e)}")
            raise RateLimitError(str(e))
        except openai.AuthenticationError as e:
            logger.error(f"Authentication error: {str(e)}")
            raise AuthError(str(e))
        except openai.BadRequestError as e:
            logger.error(f"Bad request: {str(e)}")
            raise BadRequestError(str(e))
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            raise APILensError(str(e))

# Future: AnthropicWrapper

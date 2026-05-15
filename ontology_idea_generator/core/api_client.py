import time
import json
import anthropic
from typing import List, Tuple, Dict, Any
from .logger import logger

class AnthropicAPIClient:
    def __init__(self, api_key: str, model: str, max_tokens: int):
        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = model
        self.max_tokens = max_tokens

    def call(self, system_prompt: str, user_prompt: str) -> str:
        retries = 3
        backoff = 1
        for i in range(retries):
            try:
                message = self.client.messages.create(
                    model=self.model,
                    max_tokens=self.max_tokens,
                    system=system_prompt,
                    messages=[
                        {"role": "user", "content": user_prompt}
                    ]
                )
                return message.content[0].text
            except anthropic.RateLimitError:
                if i < retries - 1:
                    logger.warning(f"Rate limit hit, retrying in {backoff} seconds...")
                    time.sleep(backoff)
                    backoff *= 2
                else:
                    raise
            except Exception as e:
                logger.error(f"API call failed: {e}")
                raise

    def call_with_structured_output(self, system_prompt: str, user_prompt: str, schema_description: str) -> Dict[str, Any]:
        full_user_prompt = f"{user_prompt}\n\nRespond only with a JSON object that matches this schema: {schema_description}"
        response_text = self.call(system_prompt, full_user_prompt)

        # Strip markdown fences if present
        if response_text.startswith("```json"):
            response_text = response_text[7:]
        if response_text.endswith("```"):
            response_text = response_text[:-3]

        try:
            return json.loads(response_text.strip())
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse structured output: {e}")
            logger.debug(f"Raw response: {response_text}")
            raise

import os
import anthropic
from dotenv import load_dotenv
from typing import List, Dict, Any, Optional

# Load environment variables
load_dotenv()

class ClaudeClient:
    def __init__(self):
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY environment variable is not set")
        
        self.client = anthropic.Anthropic(api_key=api_key)
        self.default_model = "claude-3-sonnet-20240229"
    
    async def generate_response(
        self,
        system_prompt: str,
        user_message: str,
        model: Optional[str] = None,
        max_tokens: int = 4000
    ) -> str:
        """
        Generate a response from Claude.
        
        Args:
            system_prompt: The system prompt to guide Claude's behavior
            user_message: The user's message
            model: The Claude model to use, defaults to claude-3-sonnet
            max_tokens: Maximum tokens in the response
            
        Returns:
            Claude's response text
        """
        try:
            response = await self.client.messages.create(
                model=model or self.default_model,
                max_tokens=max_tokens,
                system=system_prompt,
                messages=[
                    {"role": "user", "content": user_message}
                ]
            )
            
            return response.content[0].text
        except Exception as e:
            print(f"Error generating response from Claude: {e}")
            raise
    
    async def analyze_with_few_shot(
        self,
        system_prompt: str,
        examples: List[Dict[str, str]],
        query: str,
        model: Optional[str] = None,
        max_tokens: int = 4000
    ) -> str:
        """
        Generate a response with few-shot examples.
        
        Args:
            system_prompt: The system prompt
            examples: List of example pairs with 'user' and 'assistant' keys
            query: The query to analyze
            model: The Claude model to use
            max_tokens: Maximum tokens in the response
            
        Returns:
            Claude's response
        """
        messages = []
        
        # Add examples as context
        for example in examples:
            messages.append({"role": "user", "content": example["user"]})
            messages.append({"role": "assistant", "content": example["assistant"]})
        
        # Add the actual query
        messages.append({"role": "user", "content": query})
        
        try:
            response = await self.client.messages.create(
                model=model or self.default_model,
                max_tokens=max_tokens,
                system=system_prompt,
                messages=messages
            )
            
            return response.content[0].text
        except Exception as e:
            print(f"Error in few-shot learning with Claude: {e}")
            raise
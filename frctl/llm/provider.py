"""LLM provider using LiteLLM for unified interface to 100+ providers."""

import os
from typing import Any, Dict, List, Optional
import litellm
from litellm import completion, completion_cost


class LLMProvider:
    """Unified LLM provider using LiteLLM.
    
    Supports 100+ providers including:
    - OpenAI (gpt-4, gpt-3.5-turbo, etc.)
    - Anthropic (claude-3-5-sonnet, claude-3-opus, etc.)
    - Cohere, Together, Replicate, Azure, AWS Bedrock, etc.
    - Local models (ollama/codellama, vllm/mistral, etc.)
    
    Features:
    - Automatic retry with exponential backoff
    - Fallback chains between providers
    - Token counting across all providers
    - Cost tracking
    - Comprehensive logging for transparency
    """
    
    def __init__(
        self,
        model: str = "gpt-4",
        temperature: float = 0.7,
        max_tokens: int = 2000,
        num_retries: int = 3,
        fallback_models: Optional[List[str]] = None,
        verbose: bool = True
    ):
        """Initialize LLM provider.
        
        Args:
            model: Model identifier (e.g., "gpt-4", "claude-3-5-sonnet", "ollama/codellama")
            temperature: Sampling temperature (0.0 to 1.0)
            max_tokens: Maximum tokens to generate
            num_retries: Number of retries on failure
            fallback_models: List of fallback models if primary fails
            verbose: Enable detailed logging for transparency
        """
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.num_retries = num_retries
        self.fallback_models = fallback_models or []
        
        # Enable verbose logging for transparency
        litellm.set_verbose = verbose
        
        # Track usage statistics
        self.total_tokens = 0
        self.total_cost = 0.0
        self.call_count = 0
    
    def generate(
        self,
        messages: List[Dict[str, str]],
        **kwargs
    ) -> Dict[str, Any]:
        """Generate completion from LLM.
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            **kwargs: Additional parameters for litellm.completion()
            
        Returns:
            Response dict with 'content', 'model', 'usage', 'cost'
            
        Raises:
            Exception: If all retry attempts fail
        """
        # Merge kwargs with defaults
        params = {
            "model": self.model,
            "messages": messages,
            "temperature": kwargs.get("temperature", self.temperature),
            "max_tokens": kwargs.get("max_tokens", self.max_tokens),
            "num_retries": self.num_retries,
        }
        
        # Add fallback chain if configured
        if self.fallback_models:
            params["fallbacks"] = self.fallback_models
        
        try:
            # Call LiteLLM (handles retries, fallbacks, etc.)
            response = completion(**params)
            
            # Extract content
            content = response.choices[0].message.content
            
            # Track usage
            usage = response.usage
            self.total_tokens += usage.total_tokens
            self.call_count += 1
            
            # Calculate cost
            cost = completion_cost(response)
            self.total_cost += cost
            
            return {
                "content": content,
                "model": response.model,
                "usage": {
                    "prompt_tokens": usage.prompt_tokens,
                    "completion_tokens": usage.completion_tokens,
                    "total_tokens": usage.total_tokens,
                },
                "cost": cost,
            }
            
        except Exception as e:
            # Log error and re-raise
            print(f"LLM generation failed: {e}")
            raise
    
    def count_tokens(self, text: str, model: Optional[str] = None) -> int:
        """Count tokens in text for the specified model.
        
        Args:
            text: Text to count tokens for
            model: Model to use for counting (defaults to self.model)
            
        Returns:
            Number of tokens
        """
        model_to_use = model or self.model
        try:
            return litellm.token_counter(model=model_to_use, text=text)
        except Exception:
            # Fallback to rough estimate if model not supported
            # ~4 characters per token is a common heuristic
            return len(text) // 4
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get usage statistics for this provider.
        
        Returns:
            Dict with total_tokens, total_cost, call_count, avg_tokens
        """
        return {
            "total_tokens": self.total_tokens,
            "total_cost": round(self.total_cost, 4),
            "call_count": self.call_count,
            "avg_tokens": self.total_tokens // max(self.call_count, 1),
        }
    
    @classmethod
    def from_config(cls, config: Dict[str, Any]) -> "LLMProvider":
        """Create provider from configuration dict.
        
        Args:
            config: Configuration with keys: model, temperature, max_tokens, etc.
            
        Returns:
            Configured LLMProvider instance
        """
        return cls(
            model=config.get("model", "gpt-4"),
            temperature=config.get("temperature", 0.7),
            max_tokens=config.get("max_tokens", 2000),
            num_retries=config.get("num_retries", 3),
            fallback_models=config.get("fallbacks", []),
            verbose=config.get("verbose", True),
        )


def get_provider(model: Optional[str] = None, config_path: Optional[str] = None) -> LLMProvider:
    """Get LLM provider with optional model override.
    
    Loads configuration from:
    1. Config files (.frctl/config.toml or ~/.frctl/config.toml)
    2. Environment variables (higher priority)
    3. Function parameters (highest priority)
    
    Args:
        model: Override model from config/environment
        config_path: Optional path to config directory
        
    Returns:
        Configured LLMProvider
    """
    try:
        from frctl.config import get_config
        from pathlib import Path
        
        # Load configuration
        project_dir = Path(config_path) if config_path else None
        config = get_config(project_dir)
        
        # Apply model override if provided
        if model:
            config.llm.model = model
        
        # Create provider from config
        return LLMProvider(
            model=config.llm.model,
            temperature=config.llm.temperature,
            max_tokens=config.llm.max_tokens,
            num_retries=config.llm.num_retries,
            fallback_models=config.llm.fallback_models,
            verbose=config.llm.verbose,
        )
    except Exception:
        # Fallback to simple environment-based config
        model = model or os.getenv("FRCTL_LLM_MODEL", "gpt-4")
        temperature = float(os.getenv("FRCTL_LLM_TEMPERATURE", "0.7"))
        max_tokens = int(os.getenv("FRCTL_LLM_MAX_TOKENS", "2000"))
        
        return LLMProvider(
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
        )

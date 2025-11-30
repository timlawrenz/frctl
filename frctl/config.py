"""Configuration management for frctl.

Handles loading and validating configuration from:
1. .frctl/config.toml (project-level)
2. ~/.frctl/config.toml (user-level)
3. Environment variables (highest priority)
"""

import os
from pathlib import Path
from typing import Any, Dict, List, Optional
try:
    import tomllib  # Python 3.11+
except ImportError:
    import tomli as tomllib  # fallback for older Python


class ConfigurationError(Exception):
    """Raised when configuration is invalid or missing."""
    pass


class LLMConfig:
    """LLM provider configuration."""
    
    def __init__(
        self,
        model: str = "gpt-4",
        temperature: float = 0.7,
        max_tokens: int = 2000,
        num_retries: int = 3,
        fallback_models: Optional[List[str]] = None,
        verbose: bool = True,
        api_key: Optional[str] = None,
    ):
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.num_retries = num_retries
        self.fallback_models = fallback_models or []
        self.verbose = verbose
        self.api_key = api_key
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "LLMConfig":
        """Create config from dictionary."""
        return cls(
            model=data.get("model", "gpt-4"),
            temperature=data.get("temperature", 0.7),
            max_tokens=data.get("max_tokens", 2000),
            num_retries=data.get("num_retries", 3),
            fallback_models=data.get("fallback_models", []),
            verbose=data.get("verbose", True),
            api_key=data.get("api_key"),
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert config to dictionary."""
        return {
            "model": self.model,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "num_retries": self.num_retries,
            "fallback_models": self.fallback_models,
            "verbose": self.verbose,
        }
    
    def validate(self):
        """Validate configuration values.
        
        Raises:
            ConfigurationError: If configuration is invalid
        """
        if not 0.0 <= self.temperature <= 2.0:
            raise ConfigurationError(f"temperature must be 0.0-2.0, got {self.temperature}")
        
        if self.max_tokens <= 0:
            raise ConfigurationError(f"max_tokens must be positive, got {self.max_tokens}")
        
        if self.num_retries < 0:
            raise ConfigurationError(f"num_retries must be non-negative, got {self.num_retries}")


class PlanningConfig:
    """Planning engine configuration."""
    
    def __init__(
        self,
        max_depth: int = 10,
        auto_decompose: bool = False,
        context_window_size: int = 128000,
    ):
        self.max_depth = max_depth
        self.auto_decompose = auto_decompose
        self.context_window_size = context_window_size
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PlanningConfig":
        """Create config from dictionary."""
        return cls(
            max_depth=data.get("max_depth", 10),
            auto_decompose=data.get("auto_decompose", False),
            context_window_size=data.get("context_window_size", 128000),
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert config to dictionary."""
        return {
            "max_depth": self.max_depth,
            "auto_decompose": self.auto_decompose,
            "context_window_size": self.context_window_size,
        }
    
    def validate(self):
        """Validate configuration values.
        
        Raises:
            ConfigurationError: If configuration is invalid
        """
        if self.max_depth <= 0:
            raise ConfigurationError(f"max_depth must be positive, got {self.max_depth}")
        
        if self.context_window_size <= 0:
            raise ConfigurationError(f"context_window_size must be positive, got {self.context_window_size}")


class FrctlConfig:
    """Main frctl configuration."""
    
    def __init__(
        self,
        llm: Optional[LLMConfig] = None,
        planning: Optional[PlanningConfig] = None,
    ):
        self.llm = llm or LLMConfig()
        self.planning = planning or PlanningConfig()
    
    @classmethod
    def load(cls, project_dir: Optional[Path] = None) -> "FrctlConfig":
        """Load configuration from files and environment.
        
        Priority (highest to lowest):
        1. Environment variables
        2. Project config (.frctl/config.toml)
        3. User config (~/.frctl/config.toml)
        4. Defaults
        
        Args:
            project_dir: Project directory (defaults to cwd)
            
        Returns:
            Merged configuration
        """
        config_data: Dict[str, Any] = {"llm": {}, "planning": {}}
        
        # Load user-level config
        user_config = Path.home() / ".frctl" / "config.toml"
        if user_config.exists():
            with open(user_config, "rb") as f:
                user_data = tomllib.load(f)
                config_data = cls._merge_config(config_data, user_data)
        
        # Load project-level config
        if project_dir is None:
            project_dir = Path.cwd()
        project_config = project_dir / ".frctl" / "config.toml"
        if project_config.exists():
            with open(project_config, "rb") as f:
                project_data = tomllib.load(f)
                config_data = cls._merge_config(config_data, project_data)
        
        # Override with environment variables
        config_data = cls._apply_env_overrides(config_data)
        
        # Create config objects
        llm_config = LLMConfig.from_dict(config_data.get("llm", {}))
        planning_config = PlanningConfig.from_dict(config_data.get("planning", {}))
        
        config = cls(llm=llm_config, planning=planning_config)
        config.validate()
        
        return config
    
    @staticmethod
    def _merge_config(base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
        """Merge configuration dictionaries."""
        result = base.copy()
        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = FrctlConfig._merge_config(result[key], value)
            else:
                result[key] = value
        return result
    
    @staticmethod
    def _apply_env_overrides(config: Dict[str, Any]) -> Dict[str, Any]:
        """Apply environment variable overrides.
        
        Environment variables:
        - FRCTL_LLM_MODEL: LLM model name
        - FRCTL_LLM_TEMPERATURE: Temperature (0.0-2.0)
        - FRCTL_LLM_MAX_TOKENS: Max tokens
        - FRCTL_LLM_VERBOSE: Verbose logging (true/false)
        - OPENAI_API_KEY: OpenAI API key
        - ANTHROPIC_API_KEY: Anthropic API key
        - GEMINI_API_KEY: Google Gemini API key
        - (and all other LiteLLM-supported env vars)
        """
        llm = config.setdefault("llm", {})
        
        # Model configuration
        if model := os.getenv("FRCTL_LLM_MODEL"):
            llm["model"] = model
        
        if temp := os.getenv("FRCTL_LLM_TEMPERATURE"):
            llm["temperature"] = float(temp)
        
        if max_tokens := os.getenv("FRCTL_LLM_MAX_TOKENS"):
            llm["max_tokens"] = int(max_tokens)
        
        if verbose := os.getenv("FRCTL_LLM_VERBOSE"):
            llm["verbose"] = verbose.lower() in ("true", "1", "yes")
        
        # API keys (LiteLLM reads these directly, but we track them)
        # Common provider keys
        if api_key := (
            os.getenv("OPENAI_API_KEY") or
            os.getenv("ANTHROPIC_API_KEY") or
            os.getenv("GEMINI_API_KEY") or
            os.getenv("COHERE_API_KEY") or
            os.getenv("TOGETHER_API_KEY")
        ):
            llm["api_key"] = api_key
        
        # Planning configuration
        planning = config.setdefault("planning", {})
        
        if max_depth := os.getenv("FRCTL_PLANNING_MAX_DEPTH"):
            planning["max_depth"] = int(max_depth)
        
        if auto := os.getenv("FRCTL_PLANNING_AUTO_DECOMPOSE"):
            planning["auto_decompose"] = auto.lower() in ("true", "1", "yes")
        
        return config
    
    def validate(self):
        """Validate all configuration sections.
        
        Raises:
            ConfigurationError: If any section is invalid
        """
        self.llm.validate()
        self.planning.validate()
    
    def save(self, path: Path):
        """Save configuration to TOML file.
        
        Args:
            path: Path to config file
        """
        # Ensure directory exists
        path.parent.mkdir(parents=True, exist_ok=True)
        
        # Convert to TOML-compatible dict
        config_dict = {
            "llm": self.llm.to_dict(),
            "planning": self.planning.to_dict(),
        }
        
        # Write TOML (simple approach - could use toml library for better formatting)
        with open(path, "w") as f:
            f.write("# Frctl Configuration\n\n")
            
            f.write("[llm]\n")
            for key, value in config_dict["llm"].items():
                if isinstance(value, str):
                    f.write(f'{key} = "{value}"\n')
                elif isinstance(value, list):
                    f.write(f'{key} = {value}\n')
                else:
                    f.write(f'{key} = {value}\n')
            
            f.write("\n[planning]\n")
            for key, value in config_dict["planning"].items():
                if isinstance(value, str):
                    f.write(f'{key} = "{value}"\n')
                else:
                    f.write(f'{key} = {value}\n')


def get_config(project_dir: Optional[Path] = None) -> FrctlConfig:
    """Get current frctl configuration.
    
    This is the main entry point for accessing configuration.
    
    Args:
        project_dir: Project directory (defaults to cwd)
        
    Returns:
        Loaded and validated configuration
    """
    return FrctlConfig.load(project_dir)

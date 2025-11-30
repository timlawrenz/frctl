"""Tests for configuration management."""
import os
import pytest
from pathlib import Path
from frctl.config import (
    FrctlConfig,
    LLMConfig,
    PlanningConfig,
    ConfigurationError,
    get_config,
)


class TestLLMConfig:
    """Test LLM configuration."""
    
    def test_default_config(self):
        """Test default LLM configuration."""
        config = LLMConfig()
        assert config.model == "gpt-4"
        assert config.temperature == 0.7
        assert config.max_tokens == 2000
        assert config.num_retries == 3
        assert config.fallback_models == []
        assert config.verbose is True
    
    def test_custom_config(self):
        """Test custom LLM configuration."""
        config = LLMConfig(
            model="claude-3-5-sonnet-20241022",
            temperature=0.5,
            max_tokens=4000,
            num_retries=5,
            fallback_models=["gpt-4"],
            verbose=False,
        )
        assert config.model == "claude-3-5-sonnet-20241022"
        assert config.temperature == 0.5
        assert config.max_tokens == 4000
        assert config.num_retries == 5
        assert config.fallback_models == ["gpt-4"]
        assert config.verbose is False
    
    def test_from_dict(self):
        """Test creating config from dictionary."""
        data = {
            "model": "gpt-3.5-turbo",
            "temperature": 0.9,
            "max_tokens": 1000,
        }
        config = LLMConfig.from_dict(data)
        assert config.model == "gpt-3.5-turbo"
        assert config.temperature == 0.9
        assert config.max_tokens == 1000
        assert config.num_retries == 3  # default
    
    def test_to_dict(self):
        """Test converting config to dictionary."""
        config = LLMConfig(model="gpt-4", temperature=0.8)
        data = config.to_dict()
        assert data["model"] == "gpt-4"
        assert data["temperature"] == 0.8
        assert "verbose" in data
    
    def test_validate_temperature(self):
        """Test temperature validation."""
        config = LLMConfig(temperature=2.5)
        with pytest.raises(ConfigurationError, match="temperature"):
            config.validate()
        
        config = LLMConfig(temperature=-0.1)
        with pytest.raises(ConfigurationError, match="temperature"):
            config.validate()
    
    def test_validate_max_tokens(self):
        """Test max_tokens validation."""
        config = LLMConfig(max_tokens=-1)
        with pytest.raises(ConfigurationError, match="max_tokens"):
            config.validate()
        
        config = LLMConfig(max_tokens=0)
        with pytest.raises(ConfigurationError, match="max_tokens"):
            config.validate()
    
    def test_validate_num_retries(self):
        """Test num_retries validation."""
        config = LLMConfig(num_retries=-1)
        with pytest.raises(ConfigurationError, match="num_retries"):
            config.validate()


class TestPlanningConfig:
    """Test planning configuration."""
    
    def test_default_config(self):
        """Test default planning configuration."""
        config = PlanningConfig()
        assert config.max_depth == 10
        assert config.auto_decompose is False
        assert config.context_window_size == 128000
    
    def test_custom_config(self):
        """Test custom planning configuration."""
        config = PlanningConfig(
            max_depth=20,
            auto_decompose=True,
            context_window_size=200000,
        )
        assert config.max_depth == 20
        assert config.auto_decompose is True
        assert config.context_window_size == 200000
    
    def test_from_dict(self):
        """Test creating config from dictionary."""
        data = {
            "max_depth": 15,
            "auto_decompose": True,
        }
        config = PlanningConfig.from_dict(data)
        assert config.max_depth == 15
        assert config.auto_decompose is True
        assert config.context_window_size == 128000  # default
    
    def test_validate_max_depth(self):
        """Test max_depth validation."""
        config = PlanningConfig(max_depth=0)
        with pytest.raises(ConfigurationError, match="max_depth"):
            config.validate()
        
        config = PlanningConfig(max_depth=-5)
        with pytest.raises(ConfigurationError, match="max_depth"):
            config.validate()
    
    def test_validate_context_window(self):
        """Test context_window_size validation."""
        config = PlanningConfig(context_window_size=0)
        with pytest.raises(ConfigurationError, match="context_window_size"):
            config.validate()


class TestFrctlConfig:
    """Test main configuration."""
    
    def test_default_config(self):
        """Test default configuration."""
        config = FrctlConfig()
        assert isinstance(config.llm, LLMConfig)
        assert isinstance(config.planning, PlanningConfig)
    
    def test_custom_config(self):
        """Test custom configuration."""
        llm = LLMConfig(model="claude-3-5-sonnet-20241022")
        planning = PlanningConfig(max_depth=15)
        config = FrctlConfig(llm=llm, planning=planning)
        assert config.llm.model == "claude-3-5-sonnet-20241022"
        assert config.planning.max_depth == 15
    
    def test_validate(self):
        """Test configuration validation."""
        config = FrctlConfig()
        config.validate()  # Should not raise
        
        config.llm.temperature = 3.0
        with pytest.raises(ConfigurationError):
            config.validate()
    
    def test_save_and_load(self, tmp_path):
        """Test saving and loading configuration."""
        config_path = tmp_path / "config.toml"
        
        # Create and save config
        config = FrctlConfig(
            llm=LLMConfig(model="gpt-4", temperature=0.8),
            planning=PlanningConfig(max_depth=15),
        )
        config.save(config_path)
        
        # Verify file exists
        assert config_path.exists()
        
        # Read and verify content
        content = config_path.read_text()
        assert "model = \"gpt-4\"" in content
        assert "temperature = 0.8" in content
        assert "max_depth = 15" in content
    
    def test_merge_config(self):
        """Test configuration merging."""
        base = {
            "llm": {"model": "gpt-4", "temperature": 0.7},
            "planning": {"max_depth": 10},
        }
        override = {
            "llm": {"temperature": 0.9},
            "planning": {"auto_decompose": True},
        }
        
        merged = FrctlConfig._merge_config(base, override)
        
        assert merged["llm"]["model"] == "gpt-4"
        assert merged["llm"]["temperature"] == 0.9
        assert merged["planning"]["max_depth"] == 10
        assert merged["planning"]["auto_decompose"] is True
    
    def test_env_overrides(self, monkeypatch):
        """Test environment variable overrides."""
        monkeypatch.setenv("FRCTL_LLM_MODEL", "claude-3-5-sonnet-20241022")
        monkeypatch.setenv("FRCTL_LLM_TEMPERATURE", "0.9")
        monkeypatch.setenv("FRCTL_LLM_MAX_TOKENS", "4000")
        monkeypatch.setenv("FRCTL_LLM_VERBOSE", "false")
        monkeypatch.setenv("FRCTL_PLANNING_MAX_DEPTH", "20")
        monkeypatch.setenv("FRCTL_PLANNING_AUTO_DECOMPOSE", "true")
        monkeypatch.setenv("OPENAI_API_KEY", "sk-test")
        
        config = {}
        config = FrctlConfig._apply_env_overrides(config)
        
        assert config["llm"]["model"] == "claude-3-5-sonnet-20241022"
        assert config["llm"]["temperature"] == 0.9
        assert config["llm"]["max_tokens"] == 4000
        assert config["llm"]["verbose"] is False
        assert config["llm"]["api_key"] == "sk-test"
        assert config["planning"]["max_depth"] == 20
        assert config["planning"]["auto_decompose"] is True
    
    def test_load_with_project_config(self, tmp_path, monkeypatch):
        """Test loading with project configuration."""
        # Create project config
        project_dir = tmp_path / "project"
        project_dir.mkdir()
        config_dir = project_dir / ".frctl"
        config_dir.mkdir()
        config_file = config_dir / "config.toml"
        
        config_file.write_text("""
[llm]
model = "gpt-3.5-turbo"
temperature = 0.5

[planning]
max_depth = 12
""")
        
        # Load config
        config = FrctlConfig.load(project_dir)
        
        assert config.llm.model == "gpt-3.5-turbo"
        assert config.llm.temperature == 0.5
        assert config.planning.max_depth == 12
    
    def test_load_with_user_config(self, tmp_path, monkeypatch):
        """Test loading with user configuration."""
        # Mock home directory
        home_dir = tmp_path / "home"
        home_dir.mkdir()
        monkeypatch.setenv("HOME", str(home_dir))
        
        # Create user config
        config_dir = home_dir / ".frctl"
        config_dir.mkdir()
        config_file = config_dir / "config.toml"
        
        config_file.write_text("""
[llm]
model = "claude-3-5-sonnet-20241022"
temperature = 0.6

[planning]
max_depth = 8
""")
        
        # Change Path.home() to return our test home
        monkeypatch.setattr(Path, "home", lambda: home_dir)
        
        # Load config
        config = FrctlConfig.load()
        
        assert config.llm.model == "claude-3-5-sonnet-20241022"
        assert config.llm.temperature == 0.6
        assert config.planning.max_depth == 8
    
    def test_priority_order(self, tmp_path, monkeypatch):
        """Test configuration priority: env > project > user > defaults."""
        # Setup user config
        home_dir = tmp_path / "home"
        home_dir.mkdir()
        user_config_dir = home_dir / ".frctl"
        user_config_dir.mkdir()
        user_config = user_config_dir / "config.toml"
        user_config.write_text("""
[llm]
model = "user-model"
temperature = 0.5
""")
        
        # Setup project config
        project_dir = tmp_path / "project"
        project_dir.mkdir()
        project_config_dir = project_dir / ".frctl"
        project_config_dir.mkdir()
        project_config = project_config_dir / "config.toml"
        project_config.write_text("""
[llm]
model = "project-model"
max_tokens = 3000
""")
        
        # Setup env vars
        monkeypatch.setenv("FRCTL_LLM_TEMPERATURE", "0.9")
        monkeypatch.setattr(Path, "home", lambda: home_dir)
        
        # Load config
        config = FrctlConfig.load(project_dir)
        
        # Verify priority: env > project > user > default
        assert config.llm.model == "project-model"  # project overrides user
        assert config.llm.temperature == 0.9  # env overrides all
        assert config.llm.max_tokens == 3000  # project value
        assert config.llm.num_retries == 3  # default value


class TestGetConfig:
    """Test get_config helper function."""
    
    def test_get_config_default(self):
        """Test getting default config."""
        config = get_config()
        assert isinstance(config, FrctlConfig)
        assert config.llm.model in ["gpt-4", "claude-3-5-sonnet-20241022", "gemini/gemini-1.5-pro"]  # or env override

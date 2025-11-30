# Configuration Guide

This guide explains how to configure frctl's LLM providers and planning engine.

## Configuration Files

frctl uses TOML configuration files with the following priority (highest to lowest):

1. **Environment variables** - Override everything
2. **Project config** - `.frctl/config.toml` in your project directory
3. **User config** - `~/.frctl/config.toml` for your user
4. **Defaults** - Built-in sensible defaults

## Quick Start

### 1. Initialize Configuration

Create a config file with default settings:

```bash
# For your current project
frctl config init

# For all your projects (global)
frctl config init --global
```

This creates a config file with sensible defaults that you can customize.

### 2. Set Your API Key

The easiest way is via environment variables:

```bash
# For OpenAI
export OPENAI_API_KEY=sk-...

# For Anthropic (Claude)
export ANTHROPIC_API_KEY=sk-ant-...

# For Google Gemini
export GEMINI_API_KEY=...

# For Cohere
export COHERE_API_KEY=...
```

**⚠️ Never commit API keys to version control!**

### 3. Choose Your Model

Edit `.frctl/config.toml` or set environment variable:

```bash
# Via environment variable
export FRCTL_LLM_MODEL=claude-3-5-sonnet-20241022

# Or via frctl command
frctl config init  # then edit .frctl/config.toml
```

### 4. Test Your Configuration

```bash
frctl config test
```

This sends a simple test request to verify your API key and model work correctly.

## Configuration Reference

### LLM Settings

```toml
[llm]
# Model identifier - see supported models below
model = "gpt-4"

# Temperature (0.0 = deterministic, 2.0 = very random)
temperature = 0.7

# Maximum tokens to generate per request
max_tokens = 2000

# Number of retries on API failures
num_retries = 3

# Fallback models if primary fails (optional)
fallback_models = ["claude-3-5-sonnet-20241022", "gpt-3.5-turbo"]

# Enable verbose logging for transparency
verbose = true
```

### Planning Settings

```toml
[planning]
# Maximum planning depth (prevents infinite recursion)
max_depth = 10

# Auto-decompose goals without prompting (default: false for safety)
auto_decompose = false

# Context window size in tokens (model-dependent)
context_window_size = 128000
```

### Environment Variables

All settings can be overridden via environment variables:

```bash
# LLM Settings
export FRCTL_LLM_MODEL=gpt-4
export FRCTL_LLM_TEMPERATURE=0.7
export FRCTL_LLM_MAX_TOKENS=2000
export FRCTL_LLM_VERBOSE=true

# Planning Settings
export FRCTL_PLANNING_MAX_DEPTH=10
export FRCTL_PLANNING_AUTO_DECOMPOSE=false

# API Keys (provider-specific)
export OPENAI_API_KEY=sk-...
export ANTHROPIC_API_KEY=sk-ant-...
export GEMINI_API_KEY=...
```

## Supported Models

frctl uses LiteLLM, which supports 100+ providers. Here are some popular options:

### OpenAI

```toml
[llm]
model = "gpt-4"                    # GPT-4 (recommended)
# model = "gpt-4-turbo"            # GPT-4 Turbo (faster, cheaper)
# model = "gpt-3.5-turbo"          # GPT-3.5 (fast, cheap)
```

Set `OPENAI_API_KEY` environment variable.

### Anthropic (Claude)

```toml
[llm]
model = "claude-3-5-sonnet-20241022"  # Claude 3.5 Sonnet (excellent)
# model = "claude-3-opus-20240229"    # Claude 3 Opus (most capable)
# model = "claude-3-sonnet-20240229"  # Claude 3 Sonnet (balanced)
```

Set `ANTHROPIC_API_KEY` environment variable.

### Google Gemini

```toml
[llm]
model = "gemini/gemini-1.5-pro"    # Gemini 1.5 Pro (huge context)
# model = "gemini/gemini-1.5-flash" # Gemini 1.5 Flash (fast)
```

Set `GEMINI_API_KEY` environment variable.

### Cohere

```toml
[llm]
model = "command-r-plus"           # Command R+ (excellent)
# model = "command-r"               # Command R (fast)
```

Set `COHERE_API_KEY` environment variable.

### Local Models (Ollama)

Run models locally without API keys:

```bash
# Install Ollama: https://ollama.ai
ollama pull codellama
```

```toml
[llm]
model = "ollama/codellama"
# model = "ollama/mistral"
# model = "ollama/llama2"
```

No API key needed! Ollama runs on your machine.

### Azure OpenAI

```toml
[llm]
model = "azure/<deployment-name>"
```

Set environment variables:
```bash
export AZURE_API_KEY=...
export AZURE_API_BASE=https://...
export AZURE_API_VERSION=2023-05-15
```

### AWS Bedrock

```toml
[llm]
model = "bedrock/anthropic.claude-v2"
```

Set AWS credentials via standard methods (aws configure, environment variables, etc.)

### Complete List

See https://docs.litellm.ai/docs/providers for the full list of 100+ supported providers.

## Context Window Sizes

Different models have different context window sizes. Set this appropriately:

```toml
[planning]
# GPT-4 Turbo
context_window_size = 128000

# Claude 3.5 Sonnet
# context_window_size = 200000

# Gemini 1.5 Pro (huge!)
# context_window_size = 1000000

# GPT-3.5 Turbo
# context_window_size = 16000
```

## Fallback Chains

Configure fallback models for reliability:

```toml
[llm]
model = "gpt-4"
fallback_models = [
    "claude-3-5-sonnet-20241022",  # Try Claude if GPT-4 fails
    "gpt-3.5-turbo"                # Fall back to GPT-3.5 as last resort
]
```

frctl will automatically try fallback models if the primary fails.

## Cost Tracking

frctl automatically tracks token usage and costs:

```bash
# Test your configuration and see costs
frctl config test

# Output shows:
# ✓ Tokens: 42
# ✓ Cost: $0.0021
```

Use `verbose = true` to see detailed cost breakdowns during planning.

## Example Configurations

### Best for Quality (GPT-4)

```toml
[llm]
model = "gpt-4"
temperature = 0.7
max_tokens = 2000
fallback_models = ["claude-3-5-sonnet-20241022"]

[planning]
max_depth = 10
context_window_size = 128000
```

### Best for Speed (GPT-3.5)

```toml
[llm]
model = "gpt-3.5-turbo"
temperature = 0.7
max_tokens = 1500

[planning]
max_depth = 8
context_window_size = 16000
```

### Best for Large Plans (Gemini)

```toml
[llm]
model = "gemini/gemini-1.5-pro"
temperature = 0.7
max_tokens = 2000

[planning]
max_depth = 15
context_window_size = 1000000  # 1M tokens!
```

### Best for Privacy (Local)

```toml
[llm]
model = "ollama/codellama"
temperature = 0.7
max_tokens = 2000
verbose = false

[planning]
max_depth = 10
context_window_size = 4096
```

No data leaves your machine!

## CLI Commands

### Show Current Configuration

```bash
frctl config show

# Show all config sources
frctl config show --all
```

### Validate Configuration

```bash
frctl config validate
```

### Test Provider Connection

```bash
# Test with configured model
frctl config test

# Test with specific model
frctl config test --model claude-3-5-sonnet-20241022
```

### Initialize Configuration

```bash
# Project-level config
frctl config init

# User-level config
frctl config init --global

# Overwrite existing
frctl config init --force
```

## Troubleshooting

### "No API key found"

Make sure you've set the appropriate environment variable:

```bash
export OPENAI_API_KEY=sk-...
# or
export ANTHROPIC_API_KEY=sk-ant-...
# etc.
```

### "Model not found"

Check that your model name is correct. Common mistakes:

- ✅ `claude-3-5-sonnet-20241022`
- ❌ `claude-3.5-sonnet`
- ❌ `claude-sonnet`

See https://docs.litellm.ai/docs/providers for correct names.

### "Rate limit exceeded"

Configure retries and fallbacks:

```toml
[llm]
num_retries = 5
fallback_models = ["gpt-3.5-turbo"]
```

### "Context too long"

Reduce `max_tokens` or increase `context_window_size` for your model.

### Local model not working

Make sure Ollama is running:

```bash
ollama serve
```

Then verify your model is pulled:

```bash
ollama list
```

## Security Best Practices

1. **Never commit API keys** to version control
2. **Use environment variables** for sensitive data
3. **Add `.frctl/config.toml`** to `.gitignore` if it contains secrets
4. **Use project-level configs** for team settings (without secrets)
5. **Use user-level configs** for your personal API keys

Example `.gitignore`:

```gitignore
.frctl/config.toml  # If it contains API keys
.env                # Environment file
```

## Advanced: Custom Providers

LiteLLM supports custom endpoints:

```toml
[llm]
model = "openai/custom-model"
```

```bash
export OPENAI_API_BASE=https://your-custom-endpoint.com/v1
export OPENAI_API_KEY=your-key
```

See LiteLLM documentation for more advanced configurations.

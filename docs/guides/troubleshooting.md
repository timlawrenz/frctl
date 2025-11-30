# Troubleshooting Guide

Common issues and solutions when using frctl.

## Table of Contents

1. [Installation Issues](#installation-issues)
2. [Configuration Problems](#configuration-problems)
3. [LLM Provider Issues](#llm-provider-issues)
4. [Planning Engine Issues](#planning-engine-issues)
5. [Performance Problems](#performance-problems)
6. [Local Model Setup](#local-model-setup)
7. [Error Messages](#error-messages)

---

## Installation Issues

### Issue: `pip install -e .` fails with dependency errors

**Symptoms**:
```
ERROR: Could not find a version that satisfies the requirement litellm>=1.0
```

**Solution**:
```bash
# Update pip first
python3 -m pip install --upgrade pip

# Install with explicit dependency resolution
pip install -e . --use-pep517
```

**Alternative**:
```bash
# Install dependencies manually
pip install litellm>=1.0 jinja2>=3.0 click>=8.0 pydantic>=2.0

# Then install frctl
pip install -e .
```

### Issue: ImportError for `tomllib`

**Symptoms**:
```
ImportError: No module named 'tomllib'
```

**Cause**: Python < 3.11 doesn't include `tomllib`.

**Solution**:
```bash
# Install tomli backport
pip install tomli

# Or upgrade to Python 3.11+
python3.11 -m venv .venv
```

---

## Configuration Problems

### Issue: "No LLM provider configured"

**Symptoms**:
```
ConfigurationError: No LLM provider configured. Set OPENAI_API_KEY or configure provider.
```

**Solution 1**: Set environment variable
```bash
export OPENAI_API_KEY=sk-your-key-here
frctl config test
```

**Solution 2**: Create config file
```bash
frctl config init
# Edit .frctl/config.toml
# Add: [llm] \n model = "gpt-4"
```

**Solution 3**: Use local model (no API key needed)
```bash
# Start Ollama
ollama serve

# Pull a model
ollama pull codellama

# Configure frctl
echo '[llm]
model = "ollama/codellama"' > .frctl/config.toml

# Test
frctl config test
```

### Issue: Config file not found

**Symptoms**:
```
FileNotFoundError: .frctl/config.toml not found
```

**Solution**:
```bash
# Initialize config
frctl config init

# Or create manually
mkdir -p .frctl
cat > .frctl/config.toml << EOF
[llm]
model = "gpt-4"
temperature = 0.7
max_tokens = 2000

[planning]
max_depth = 10
auto_decompose = false
EOF
```

### Issue: Configuration validation fails

**Symptoms**:
```
ConfigurationError: temperature must be 0.0-2.0, got 3.5
```

**Solution**: Check config values
```bash
# View current config
frctl config show

# Validate
frctl config validate

# Fix invalid values
nano .frctl/config.toml

# Temperature: 0.0-2.0 (typically 0.3-0.9)
# Max tokens: > 0 (typically 1000-4000)
# Max depth: > 0 (typically 5-15)
```

---

## LLM Provider Issues

### Issue: API key invalid or expired

**Symptoms**:
```
AuthenticationError: Invalid API key
```

**Solution**:
```bash
# Check API key is set
echo $OPENAI_API_KEY

# Test with curl
curl https://api.openai.com/v1/models \
  -H "Authorization: Bearer $OPENAI_API_KEY"

# If invalid, get new key from:
# - OpenAI: https://platform.openai.com/api-keys
# - Anthropic: https://console.anthropic.com/
# - Google: https://makersuite.google.com/app/apikey
```

### Issue: Rate limit exceeded

**Symptoms**:
```
RateLimitError: Rate limit exceeded. Please wait.
```

**Solution 1**: Wait and retry
```bash
# Planning engine auto-retries with exponential backoff
# Just wait 1-2 minutes and try again
```

**Solution 2**: Configure fallback models
```toml
[llm]
model = "gpt-4"
fallback_models = ["gpt-3.5-turbo", "claude-3-5-sonnet-20241022"]
```

**Solution 3**: Use different provider
```bash
# Switch to Anthropic
export ANTHROPIC_API_KEY=sk-ant-your-key
frctl config init --provider anthropic
```

### Issue: Model not found

**Symptoms**:
```
NotFoundError: Model 'gpt-5' not found
```

**Solution**: Check available models
```bash
# View supported models
frctl config test --list-models

# Common models:
# - OpenAI: gpt-4, gpt-4-turbo, gpt-3.5-turbo
# - Anthropic: claude-3-5-sonnet-20241022, claude-3-opus-20240229
# - Google: gemini/gemini-1.5-pro, gemini/gemini-1.5-flash
# - Local: ollama/codellama, ollama/mistral, ollama/llama2
```

### Issue: Timeout errors

**Symptoms**:
```
TimeoutError: Request timed out after 60 seconds
```

**Solution**: Increase timeout
```toml
[llm]
timeout = 120  # seconds
num_retries = 5
```

**Alternative**: Use faster model
```toml
model = "gpt-3.5-turbo"  # Faster than gpt-4
# or
model = "gemini/gemini-1.5-flash"  # Faster than Pro
```

---

## Planning Engine Issues

### Issue: Planning gets stuck

**Symptoms**:
- `frctl plan continue` makes no progress
- Same goal keeps decomposing

**Diagnosis**:
```bash
# Check plan status
frctl plan status <plan-id> --verbose

# Look for:
# - Max depth reached
# - Circular dependencies
# - LLM returning invalid JSON
```

**Solution 1**: Max depth reached
```bash
# Increase max depth
echo '[planning]
max_depth = 15' >> .frctl/config.toml

# Continue planning
frctl plan continue <plan-id>
```

**Solution 2**: Invalid LLM responses
```bash
# Check logs
cat .frctl/logs/planning.log | grep ERROR

# Try different model
frctl plan continue <plan-id> --model claude-3-5-sonnet-20241022
```

**Solution 3**: Reset problematic goal
```python
# Manual intervention (use Python API)
from frctl.planning.persistence import PlanStore

store = PlanStore()
plan = store.load("<plan-id>")

# Find stuck goal
stuck_goal = plan.get_goal("problem-goal-id")

# Reset to pending
stuck_goal.status = "pending"
stuck_goal.child_ids = []

# Save
store.save(plan)
```

### Issue: Goals are too granular

**Symptoms**:
- 20+ sub-goals for simple tasks
- Planning tree is 10+ levels deep

**Solution**: Adjust prompts for coarser decomposition
```bash
# Create custom prompt template
cp frctl/llm/prompts/decompose_goal.j2 .frctl/prompts/decompose_goal.j2

# Edit to prefer fewer, larger sub-goals
# Change "2-7 sub-goals" to "2-4 sub-goals"
# Add examples of good granularity for your domain
```

### Issue: Goals are too high-level

**Symptoms**:
- "Atomic" goals are still complex
- Goals marked atomic but take days to implement

**Solution**: Stricter atomicity criteria
```bash
# Edit atomicity check template
cp frctl/llm/prompts/atomicity_check.j2 .frctl/prompts/atomicity_check.j2

# Change criteria:
# - "~50-200 lines of code" → "~25-100 lines"
# - "single file/component" → "single function/class"
```

### Issue: Token limit exceeded

**Symptoms**:
```
TokenLimitError: Context exceeds 128000 tokens
```

**Solution 1**: Enable aggressive digesting
```toml
[planning]
digest_threshold = 500  # Generate digest after 500 tokens per goal
compression_target = 0.10  # Target 10% size
```

**Solution 2**: Reduce global context
```python
engine.context_tree.set_global_context({
    "project": "My Project",  # Keep only essential info
    "tech": "Python"
})
```

**Solution 3**: Use model with larger context
```toml
[llm]
model = "gemini/gemini-1.5-pro"  # 1M token context
# or
model = "claude-3-5-sonnet-20241022"  # 200K token context
```

---

## Performance Problems

### Issue: Planning is slow

**Symptoms**:
- Each decomposition takes >30 seconds
- 100-goal plan takes >30 minutes

**Diagnosis**:
```bash
# Check token usage
frctl plan status <plan-id> --stats

# Look for:
# - High tokens per goal (>3000)
# - Many LLM calls per goal (>2)
# - Large global context
```

**Solution 1**: Use faster model
```toml
[llm]
model = "gpt-3.5-turbo"  # 10x faster than gpt-4
# or
model = "gemini/gemini-1.5-flash"  # Very fast
```

**Solution 2**: Reduce token usage
```toml
[llm]
max_tokens = 1000  # Lower limit (default: 2000)
temperature = 0.3  # More focused, faster responses
```

**Solution 3**: Parallel planning
```python
# TODO: Parallel decomposition coming in v0.2
# For now: split into multiple independent plans
```

### Issue: High API costs

**Symptoms**:
- $10+ for single planning session
- Thousands of tokens per goal

**Solution 1**: Use cheaper model
```toml
[llm]
model = "gpt-3.5-turbo"  # 10x cheaper than gpt-4
```

**Solution 2**: Local model (free)
```bash
# See "Local Model Setup" section below
# Ollama models are free!
```

**Solution 3**: Track and optimize
```bash
# Check cost
frctl plan status <plan-id> --cost

# Optimize prompts to reduce tokens
# Use digests aggressively
```

---

## Local Model Setup

### Ollama Installation

**Recommended for**: Free, private, offline planning.

**Step 1**: Install Ollama
```bash
# macOS
brew install ollama

# Linux
curl -fsSL https://ollama.com/install.sh | sh

# Windows
# Download from https://ollama.com/download
```

**Step 2**: Start Ollama
```bash
ollama serve
```

**Step 3**: Pull a model
```bash
# Recommended models for planning:
ollama pull codellama       # Best for code (7B)
ollama pull mistral         # General purpose (7B)
ollama pull llama2:13b      # More capable (13B)
ollama pull deepseek-coder  # Code-focused (6.7B)
```

**Step 4**: Configure frctl
```bash
# Create config
cat > .frctl/config.toml << EOF
[llm]
model = "ollama/codellama"
temperature = 0.7
max_tokens = 2000
EOF

# Test
frctl config test
```

**Step 5**: Start planning
```bash
frctl plan init "Build API server"
```

### Performance Tuning

**GPU Acceleration** (if available):
```bash
# Ollama auto-detects GPU
# Check GPU usage:
nvidia-smi  # NVIDIA
rocm-smi    # AMD
```

**Adjust context window**:
```toml
[llm]
model = "ollama/mistral"
max_tokens = 4000  # Larger for complex decompositions

[planning]
context_window_size = 32768  # Match model's context limit
```

**Model comparison**:

| Model | Speed | Quality | Size | Best For |
|-------|-------|---------|------|----------|
| codellama | Fast | Good | 3.8GB | Code planning |
| mistral | Fast | Good | 4.1GB | General planning |
| llama2:13b | Medium | Better | 7.4GB | Complex plans |
| deepseek-coder | Fast | Good | 3.7GB | Code-heavy |

### Troubleshooting Local Models

**Issue**: "Connection refused"
```bash
# Check Ollama is running
ollama list

# Start server
ollama serve

# Test
curl http://localhost:11434/api/tags
```

**Issue**: Low quality decompositions
```bash
# Try larger model
ollama pull llama2:13b

# Update config
echo 'model = "ollama/llama2:13b"' >> .frctl/config.toml
```

**Issue**: Out of memory
```bash
# Use smaller model
ollama pull codellama:7b

# Or reduce context
[planning]
context_window_size = 4096
```

---

## Error Messages

### ConfigurationError

**Message**: `No LLM provider configured`
→ See [Configuration Problems](#configuration-problems)

**Message**: `temperature must be 0.0-2.0`
→ Fix config file: `temperature = 0.7`

**Message**: `API key not found`
→ Set environment variable: `export OPENAI_API_KEY=...`

### PlanningError

**Message**: `Maximum depth exceeded`
→ Increase `max_depth` in config or simplify goal

**Message**: `No sub-goals generated`
→ LLM returned invalid response; retry or use different model

**Message**: `Circular dependency detected`
→ Manual fix required; edit plan JSON

### LLMError

**Message**: `Rate limit exceeded`
→ Wait and retry, or use fallback model

**Message**: `Invalid API key`
→ Check API key is correct and active

**Message**: `Model not found`
→ Use valid model name (see `frctl config test --list-models`)

### JSONDecodeError

**Message**: `Expecting value: line 1 column 1`
→ LLM returned non-JSON; check logs, retry

**Message**: `Invalid \escape`
→ LLM used invalid JSON escaping; retry or fix prompt

---

## Getting Help

### Debug Mode

```bash
# Enable detailed logging
export FRCTL_DEBUG=1

# Run command
frctl plan continue <plan-id>

# Check logs
cat .frctl/logs/frctl.log
```

### Logs

```bash
# Planning logs
tail -f .frctl/logs/planning.log

# LLM interaction logs
tail -f .frctl/logs/llm.log

# Error logs
grep ERROR .frctl/logs/*.log
```

### Reporting Issues

Include:
1. frctl version: `frctl --version`
2. Python version: `python --version`
3. Config: `frctl config show`
4. Error message (full traceback)
5. Plan ID (if applicable)
6. Steps to reproduce

**Submit at**: https://github.com/timlawrenz/frctl/issues

---

## Common Workflows

### Reset a failed plan

```bash
# Backup first
cp -r .frctl/plans/<plan-id>.json .frctl/plans/<plan-id>.backup.json

# Option 1: Delete and restart
frctl plan delete <plan-id>
frctl plan init "Same goal"

# Option 2: Reset to root
python3 << EOF
from frctl.planning.persistence import PlanStore
store = PlanStore()
plan = store.load("<plan-id>")
root = plan.get_goal(plan.root_goal_id)
root.status = "pending"
root.child_ids = []
for goal_id in list(plan.goals.keys()):
    if goal_id != plan.root_goal_id:
        del plan.goals[goal_id]
store.save(plan)
EOF

frctl plan continue <plan-id>
```

### Switch LLM providers mid-plan

```bash
# Continue with different model
frctl plan continue <plan-id> --model claude-3-5-sonnet-20241022

# Or update config permanently
echo 'model = "claude-3-5-sonnet-20241022"' > .frctl/config.toml
frctl plan continue <plan-id>
```

### Export plan for sharing

```bash
# Export as JSON
frctl plan export <plan-id> plan-export.json

# Share (remove sensitive info first!)
git add plan-export.json
git commit -m "Add planning for feature X"
```

---

## Performance Benchmarks

**Expected performance** (gpt-4):
- Simple goal (<10 sub-goals): 2-5 minutes
- Medium goal (10-50 sub-goals): 10-30 minutes
- Complex goal (50-100 sub-goals): 30-60 minutes

**Expected performance** (gpt-3.5-turbo):
- 3-5x faster than gpt-4
- Slightly lower quality decomposition

**Expected performance** (local models):
- 2-10x slower than cloud APIs
- Quality varies by model size
- No API costs or rate limits

---

## Best Practices

1. **Start small**: Test with simple goals before complex ones
2. **Use version control**: Track `.frctl/` directory in git
3. **Monitor costs**: Check `frctl plan status --cost` regularly
4. **Backup plans**: Copy `.frctl/plans/` before major changes
5. **Try multiple providers**: Different LLMs excel at different tasks
6. **Customize prompts**: Tailor for your domain
7. **Review decompositions**: Sanity-check LLM output
8. **Use local models**: For exploration and development

---

**Still stuck?** Open an issue: https://github.com/timlawrenz/frctl/issues

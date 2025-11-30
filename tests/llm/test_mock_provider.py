"""Mock LLM provider for deterministic testing."""

import pytest
from frctl.llm.provider import LLMProvider


class MockLLMProvider(LLMProvider):
    """Mock LLM provider that returns predefined responses.
    
    This provider is useful for deterministic testing without making actual
    API calls. It can be configured to return specific responses in sequence.
    """
    
    def __init__(self, responses=None):
        """Initialize mock provider.
        
        Args:
            responses: List of response strings to return in sequence.
                      If None, returns default empty response.
        """
        super().__init__(model="mock")
        self.responses = responses or []
        self.call_count = 0
        self.last_messages = None
        self.all_messages = []
        
    def generate(self, messages, **kwargs):
        """Generate a mock response.
        
        Args:
            messages: List of message dicts (stored for verification)
            **kwargs: Ignored for mock
            
        Returns:
            dict: Mock response in same format as real LLMProvider
        """
        self.last_messages = messages
        self.all_messages.append(messages)
        
        # Get next response or use default
        if self.call_count < len(self.responses):
            content = self.responses[self.call_count]
        else:
            content = '{"result": "mock response"}'
            
        self.call_count += 1
        
        # Count tokens (simple approximation)
        prompt_text = " ".join(msg.get("content", "") for msg in messages)
        prompt_tokens = len(prompt_text.split())
        completion_tokens = len(content.split())
        
        # Return in same format as real LLMProvider
        return {
            "content": content,
            "model": "mock",
            "usage": {
                "prompt_tokens": prompt_tokens,
                "completion_tokens": completion_tokens,
                "total_tokens": prompt_tokens + completion_tokens
            },
            "cost": 0.0
        }
    
    def count_tokens(self, text: str) -> int:
        """Mock token counting (simple word count).
        
        Args:
            text: Text to count tokens for
            
        Returns:
            int: Approximate token count (word count)
        """
        return len(text.split())
    
    def reset(self):
        """Reset the mock provider state."""
        self.call_count = 0
        self.last_messages = None
        self.all_messages = []


class TestMockProvider:
    """Tests for MockLLMProvider."""
    
    def test_create_mock_provider(self):
        """Test creating a mock provider."""
        provider = MockLLMProvider()
        assert provider.model == "mock"
        assert provider.call_count == 0
    
    def test_single_response(self):
        """Test mock provider with single response."""
        provider = MockLLMProvider(responses=['{"test": "response"}'])
        
        result = provider.generate([{"role": "user", "content": "test prompt"}])
        
        assert provider.call_count == 1
        assert provider.last_messages[0]["content"] == "test prompt"
        assert result["content"] == '{"test": "response"}'
        assert "usage" in result
        assert "cost" in result
    
    def test_multiple_responses(self):
        """Test mock provider with sequence of responses."""
        responses = [
            '{"response": 1}',
            '{"response": 2}',
            '{"response": 3}'
        ]
        provider = MockLLMProvider(responses=responses)
        
        # First call
        result1 = provider.generate([{"role": "user", "content": "prompt 1"}])
        assert result1["content"] == '{"response": 1}'
        
        # Second call
        result2 = provider.generate([{"role": "user", "content": "prompt 2"}])
        assert result2["content"] == '{"response": 2}'
        
        # Third call
        result3 = provider.generate([{"role": "user", "content": "prompt 3"}])
        assert result3["content"] == '{"response": 3}'
        
        assert provider.call_count == 3
        assert len(provider.all_messages) == 3
    
    def test_default_response(self):
        """Test default response when no responses configured."""
        provider = MockLLMProvider()
        
        result = provider.generate([{"role": "user", "content": "test"}])
        
        assert '{"result": "mock response"}' in result["content"]
    
    def test_exhausted_responses(self):
        """Test behavior when responses are exhausted."""
        provider = MockLLMProvider(responses=['{"first": "response"}'])
        
        # First call uses configured response
        result1 = provider.generate([{"role": "user", "content": "test 1"}])
        assert result1["content"] == '{"first": "response"}'
        
        # Second call uses default
        result2 = provider.generate([{"role": "user", "content": "test 2"}])
        assert '{"result": "mock response"}' in result2["content"]
    
    def test_token_counting(self):
        """Test mock token counting."""
        provider = MockLLMProvider()
        
        # Simple word-based counting
        assert provider.count_tokens("hello world") == 2
        assert provider.count_tokens("one two three four") == 4
    
    def test_reset(self):
        """Test resetting provider state."""
        provider = MockLLMProvider(responses=['{"test": "response"}'])
        
        # Make a call
        provider.generate([{"role": "user", "content": "test"}])
        assert provider.call_count == 1
        assert provider.last_messages is not None
        assert len(provider.all_messages) == 1
        
        # Reset
        provider.reset()
        assert provider.call_count == 0
        assert provider.last_messages is None
        assert len(provider.all_messages) == 0
    
    def test_usage_stats(self):
        """Test that usage stats are included."""
        provider = MockLLMProvider(responses=['{"test": "response"}'])
        
        result = provider.generate([{"role": "user", "content": "hello world"}])
        
        assert "usage" in result
        assert "prompt_tokens" in result["usage"]
        assert "completion_tokens" in result["usage"]
        assert "total_tokens" in result["usage"]
        assert result["usage"]["total_tokens"] == (
            result["usage"]["prompt_tokens"] + result["usage"]["completion_tokens"]
        )

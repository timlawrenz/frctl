"""Tests for prompt template rendering."""

import pytest
from pathlib import Path
from frctl.llm.renderer import PromptRenderer, get_renderer


class TestPromptRenderer:
    """Test suite for PromptRenderer."""
    
    def test_renderer_initialization(self):
        """Test renderer initializes with default template directory."""
        renderer = PromptRenderer()
        assert renderer.template_dir.exists()
        assert renderer.template_dir.name == "prompts"
    
    def test_custom_template_directory(self, tmp_path):
        """Test renderer can use custom template directory."""
        custom_dir = tmp_path / "custom_templates"
        custom_dir.mkdir()
        
        # Create a test template
        (custom_dir / "test.j2").write_text("Hello {{ name }}!")
        
        renderer = PromptRenderer(template_dir=custom_dir)
        result = renderer.render("test", name="World")
        assert result == "Hello World!"
    
    def test_list_templates(self):
        """Test listing available templates."""
        renderer = PromptRenderer()
        templates = renderer.list_templates()
        
        assert isinstance(templates, list)
        assert "atomicity_check" in templates
        assert "decompose_goal" in templates
        assert "system_base" in templates
        assert "infer_dependencies" in templates
        assert "generate_digest" in templates
    
    def test_render_system_prompt(self):
        """Test rendering system prompt."""
        renderer = PromptRenderer()
        prompt = renderer.render_system_prompt()
        
        assert "Fractal V3" in prompt
        assert "Recursive Decomposition" in prompt
        assert "Context Awareness" in prompt
    
    def test_render_atomicity_check_minimal(self):
        """Test rendering atomicity check with minimal context."""
        renderer = PromptRenderer()
        prompt = renderer.render_atomicity_check(
            goal_description="Add user authentication"
        )
        
        assert "Add user authentication" in prompt
        assert "atomic" in prompt.lower()
        assert "composite" in prompt.lower()
        assert "JSON" in prompt
    
    def test_render_atomicity_check_with_context(self):
        """Test rendering atomicity check with full context."""
        renderer = PromptRenderer()
        prompt = renderer.render_atomicity_check(
            goal_description="Add user authentication",
            parent_intent="Build user management system",
            global_context="Project: SaaS platform\nTech: Python/FastAPI"
        )
        
        assert "Add user authentication" in prompt
        assert "Build user management system" in prompt
        assert "SaaS platform" in prompt
        assert "Python/FastAPI" in prompt
    
    def test_render_decompose_goal_minimal(self):
        """Test rendering decompose goal with minimal context."""
        renderer = PromptRenderer()
        prompt = renderer.render_decompose_goal(
            goal_description="Build payment processing"
        )
        
        assert "Build payment processing" in prompt
        assert "sub-goals" in prompt.lower()
        assert "2-7" in prompt
        assert "JSON" in prompt
    
    def test_render_decompose_goal_with_context(self):
        """Test rendering decompose goal with full context."""
        renderer = PromptRenderer()
        prompt = renderer.render_decompose_goal(
            goal_description="Build payment processing",
            parent_intent="Create e-commerce platform",
            global_context="Budget: $50k\nTimeline: Q1 2024"
        )
        
        assert "Build payment processing" in prompt
        assert "Create e-commerce platform" in prompt
        assert "Budget: $50k" in prompt
        assert "Timeline: Q1 2024" in prompt
    
    def test_render_infer_dependencies(self):
        """Test rendering dependency inference prompt."""
        renderer = PromptRenderer()
        
        sibling_goals = [
            {"id": "g1", "description": "Create database schema"},
            {"id": "g2", "description": "Implement API endpoints"},
            {"id": "g3", "description": "Add UI components"},
        ]
        
        prompt = renderer.render_infer_dependencies(
            sibling_goals=sibling_goals,
            parent_intent="Build user management"
        )
        
        assert "Create database schema" in prompt
        assert "Implement API endpoints" in prompt
        assert "Add UI components" in prompt
        assert "g1" in prompt
        assert "g2" in prompt
        assert "g3" in prompt
        assert "Build user management" in prompt
        assert "dependencies" in prompt.lower()
    
    def test_render_generate_digest_minimal(self):
        """Test rendering digest generation with minimal info."""
        renderer = PromptRenderer()
        prompt = renderer.render_generate_digest(
            goal_description="Implement JWT authentication",
            goal_status="COMPLETE"
        )
        
        assert "Implement JWT authentication" in prompt
        assert "COMPLETE" in prompt
        assert "digest" in prompt.lower()
        assert "JSON" in prompt
    
    def test_render_generate_digest_with_results(self):
        """Test rendering digest generation with full info."""
        renderer = PromptRenderer()
        prompt = renderer.render_generate_digest(
            goal_description="Implement JWT authentication",
            goal_status="COMPLETE",
            goal_results="Created auth module, 15 tests passing",
            child_digests=[
                "JWT token generation complete with HS256",
                "Token validation with expiry checking done"
            ],
            parent_intent="Build secure user authentication"
        )
        
        assert "Implement JWT authentication" in prompt
        assert "COMPLETE" in prompt
        assert "Created auth module" in prompt
        assert "JWT token generation" in prompt
        assert "Token validation" in prompt
        assert "Build secure user authentication" in prompt
    
    def test_template_caching(self):
        """Test that templates are cached after first load."""
        renderer = PromptRenderer()
        
        # First render
        prompt1 = renderer.render_system_prompt()
        cache_size_1 = len(renderer._template_cache)
        
        # Second render (should use cache)
        prompt2 = renderer.render_system_prompt()
        cache_size_2 = len(renderer._template_cache)
        
        assert prompt1 == prompt2
        assert cache_size_1 == cache_size_2
        assert "system_base.j2" in renderer._template_cache
    
    def test_template_not_found(self):
        """Test error handling for missing templates."""
        renderer = PromptRenderer()
        
        with pytest.raises(Exception):  # TemplateNotFound
            renderer.render("nonexistent_template")
    
    def test_validate_template_exists(self):
        """Test validating existing template."""
        renderer = PromptRenderer()
        assert renderer.validate_template("system_base") is True
        assert renderer.validate_template("atomicity_check") is True
    
    def test_validate_template_not_exists(self):
        """Test validating nonexistent template."""
        renderer = PromptRenderer()
        assert renderer.validate_template("nonexistent") is False
    
    def test_get_renderer_singleton(self):
        """Test that get_renderer returns singleton instance."""
        renderer1 = get_renderer()
        renderer2 = get_renderer()
        
        assert renderer1 is renderer2
    
    def test_render_with_extension(self):
        """Test that render works with .j2 extension."""
        renderer = PromptRenderer()
        
        prompt1 = renderer.render("system_base")
        prompt2 = renderer.render("system_base.j2")
        
        assert prompt1 == prompt2
    
    def test_jinja2_whitespace_handling(self):
        """Test that Jinja2 whitespace control works correctly."""
        renderer = PromptRenderer()
        
        # Render with optional sections
        prompt = renderer.render_atomicity_check(
            goal_description="Test goal"
        )
        
        # Should not have extra blank lines from missing optional sections
        assert "\n\n\n" not in prompt
    
    def test_all_templates_renderable(self):
        """Test that all templates can be rendered without errors."""
        renderer = PromptRenderer()
        templates = renderer.list_templates()
        
        errors = []
        for template_name in templates:
            try:
                # Try rendering with minimal required context
                if template_name == "atomicity_check":
                    renderer.render_atomicity_check(goal_description="test")
                elif template_name == "decompose_goal":
                    renderer.render_decompose_goal(goal_description="test")
                elif template_name == "infer_dependencies":
                    renderer.render_infer_dependencies(sibling_goals=[])
                elif template_name == "generate_digest":
                    renderer.render_generate_digest(
                        goal_description="test", goal_status="COMPLETE"
                    )
                elif template_name == "system_base":
                    renderer.render_system_prompt()
                else:
                    renderer.render(template_name)
            except Exception as e:
                errors.append(f"{template_name}: {e}")
        
        assert not errors, f"Templates failed to render: {errors}"

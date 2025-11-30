"""Prompt template rendering and management for Fractal V3 planning system."""

from pathlib import Path
from typing import Dict, Any, Optional
from jinja2 import Environment, FileSystemLoader, Template, TemplateNotFound


class PromptRenderer:
    """Manages and renders Jinja2 prompt templates.
    
    Provides a clean interface for loading and rendering prompts with
    proper context injection and error handling.
    """
    
    # Template version for cache invalidation
    VERSION = "1.0.0"
    
    def __init__(self, template_dir: Optional[Path] = None):
        """Initialize prompt renderer.
        
        Args:
            template_dir: Directory containing .j2 template files
                         (defaults to frctl/llm/prompts/)
        """
        if template_dir is None:
            # Default to prompts directory relative to this file
            template_dir = Path(__file__).parent / "prompts"
        
        self.template_dir = Path(template_dir)
        
        # Create Jinja2 environment with safe defaults
        self.env = Environment(
            loader=FileSystemLoader(str(self.template_dir)),
            autoescape=False,  # We're generating prompts, not HTML
            trim_blocks=True,
            lstrip_blocks=True,
        )
        
        # Cache for loaded templates
        self._template_cache: Dict[str, Template] = {}
    
    def render(self, template_name: str, **context: Any) -> str:
        """Render a prompt template with the given context.
        
        Args:
            template_name: Name of template file (without .j2 extension)
            **context: Template variables to inject
            
        Returns:
            Rendered prompt string
            
        Raises:
            TemplateNotFound: If template doesn't exist
            
        Example:
            >>> renderer = PromptRenderer()
            >>> prompt = renderer.render(
            ...     "atomicity_check",
            ...     goal_description="Build user auth",
            ...     parent_intent="Create user management system"
            ... )
        """
        # Add .j2 extension if not present
        if not template_name.endswith('.j2'):
            template_name = f"{template_name}.j2"
        
        # Load template (cached after first load)
        if template_name not in self._template_cache:
            try:
                self._template_cache[template_name] = self.env.get_template(template_name)
            except TemplateNotFound:
                raise TemplateNotFound(
                    f"Template '{template_name}' not found in {self.template_dir}"
                )
        
        template = self._template_cache[template_name]
        
        # Render with context
        return template.render(**context)
    
    def render_system_prompt(self, base: str = "system_base") -> str:
        """Render a system-level prompt.
        
        Args:
            base: Base system template name (default: system_base)
            
        Returns:
            Rendered system prompt
        """
        return self.render(base)
    
    def render_atomicity_check(
        self,
        goal_description: str,
        parent_intent: Optional[str] = None,
        global_context: Optional[str] = None,
    ) -> str:
        """Render atomicity check prompt.
        
        Args:
            goal_description: Description of the goal to assess
            parent_intent: Optional parent goal context
            global_context: Optional project-level context
            
        Returns:
            Rendered prompt for atomicity assessment
        """
        return self.render(
            "atomicity_check",
            goal_description=goal_description,
            parent_intent=parent_intent,
            global_context=global_context,
        )
    
    def render_decompose_goal(
        self,
        goal_description: str,
        parent_intent: Optional[str] = None,
        global_context: Optional[str] = None,
    ) -> str:
        """Render goal decomposition prompt.
        
        Args:
            goal_description: Description of the goal to decompose
            parent_intent: Optional parent goal context
            global_context: Optional project-level context
            
        Returns:
            Rendered prompt for goal decomposition
        """
        return self.render(
            "decompose_goal",
            goal_description=goal_description,
            parent_intent=parent_intent,
            global_context=global_context,
        )
    
    def render_infer_dependencies(
        self,
        sibling_goals: list,
        parent_intent: Optional[str] = None,
        global_context: Optional[str] = None,
    ) -> str:
        """Render dependency inference prompt.
        
        Args:
            sibling_goals: List of goal objects with id and description
            parent_intent: Optional parent goal context
            global_context: Optional project-level context
            
        Returns:
            Rendered prompt for dependency analysis
        """
        return self.render(
            "infer_dependencies",
            sibling_goals=sibling_goals,
            parent_intent=parent_intent,
            global_context=global_context,
        )
    
    def render_generate_digest(
        self,
        goal_description: str,
        goal_status: str,
        goal_results: Optional[str] = None,
        child_digests: Optional[list] = None,
        parent_intent: Optional[str] = None,
    ) -> str:
        """Render digest generation prompt.
        
        Args:
            goal_description: Description of completed goal
            goal_status: Status of the goal
            goal_results: Optional results or output
            child_digests: Optional list of child goal digests
            parent_intent: Optional parent goal context
            
        Returns:
            Rendered prompt for digest generation
        """
        return self.render(
            "generate_digest",
            goal_description=goal_description,
            goal_status=goal_status,
            goal_results=goal_results,
            child_digests=child_digests or [],
            parent_intent=parent_intent,
        )
    
    def list_templates(self) -> list[str]:
        """List all available template names.
        
        Returns:
            List of template names (without .j2 extension)
        """
        templates = []
        for path in self.template_dir.glob("*.j2"):
            templates.append(path.stem)
        return sorted(templates)
    
    def validate_template(self, template_name: str) -> bool:
        """Validate that a template exists and can be loaded.
        
        Args:
            template_name: Name of template to validate
            
        Returns:
            True if template is valid, False otherwise
        """
        try:
            self.render(template_name)
            return True
        except TemplateNotFound:
            return False


# Singleton instance for easy import
_default_renderer: Optional[PromptRenderer] = None

def get_renderer() -> PromptRenderer:
    """Get the default prompt renderer instance.
    
    Returns:
        Shared PromptRenderer instance
    """
    global _default_renderer
    if _default_renderer is None:
        _default_renderer = PromptRenderer()
    return _default_renderer

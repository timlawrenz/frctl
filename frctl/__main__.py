"""Main entry point for the frctl CLI."""
import click
import os
from pathlib import Path

from frctl.graph import FederatedGraph, Node, NodeType, Edge, EdgeType
from frctl.graph.dag import generate_purl
from frctl.planning.engine import PlanningEngine
from frctl.llm.provider import get_provider


@click.group()
def cli():
    """frctl - Fractal project management tool"""
    pass


@cli.group()
def graph():
    """Manage the architectural graph"""
    pass


@cli.group()
def plan():
    """Manage planning sessions"""
    pass


@graph.command("init")
def graph_init():
    """Initialize an empty graph"""
    frctl_dir = Path(".frctl")
    frctl_dir.mkdir(exist_ok=True)
    
    graph_path = frctl_dir / "graph.json"
    
    if graph_path.exists():
        click.echo(f"Graph already exists at {graph_path}")
        return
    
    g = FederatedGraph()
    g.save(graph_path)
    
    click.echo(f"✓ Initialized empty graph at {graph_path}")


@graph.command("show")
def graph_show():
    """Display graph structure"""
    graph_path = Path(".frctl/graph.json")
    
    if not graph_path.exists():
        click.echo("No graph found. Run 'frctl graph init' first.")
        return
    
    g = FederatedGraph.load(graph_path)
    
    click.echo(f"\nGraph Statistics:")
    click.echo(f"  Nodes: {g.node_count()}")
    click.echo(f"  Edges: {g.edge_count()}")
    click.echo(f"  Depth: {g.depth()}")
    click.echo(f"  Hash:  {g.merkle_hash()[:16]}...")
    
    if g.node_count() > 0:
        click.echo(f"\nNodes:")
        for node_id in sorted(g.nodes.keys()):
            node = g.nodes[node_id]
            click.echo(f"  - {node.type.value:10} {node.name:20} ({node_id})")
    
    if g.edge_count() > 0:
        click.echo(f"\nEdges:")
        for edge in sorted(g.edges, key=lambda e: (e.source, e.target)):
            click.echo(f"  - {edge.source} --[{edge.edge_type.value}]--> {edge.target}")


@graph.command("add-node")
@click.argument("node_type")
@click.argument("name")
def graph_add_node(node_type: str, name: str):
    """Add a node to the graph"""
    graph_path = Path(".frctl/graph.json")
    
    if not graph_path.exists():
        click.echo("No graph found. Run 'frctl graph init' first.")
        return
    
    # Validate node type
    try:
        ntype = NodeType(node_type)
    except ValueError:
        click.echo(f"Invalid node type: {node_type}")
        click.echo(f"Valid types: {', '.join([t.value for t in NodeType])}")
        return
    
    g = FederatedGraph.load(graph_path)
    
    # Generate PURL
    node_id = generate_purl(name)
    
    # Check if node already exists
    if node_id in g.nodes:
        click.echo(f"Node with ID '{node_id}' already exists")
        return
    
    # Create and add node
    node = Node(id=node_id, type=ntype, name=name)
    g.add_node(node)
    
    # Save graph
    g.save(graph_path)
    
    click.echo(f"✓ Added {ntype.value} node: {name} ({node_id})")


@graph.command("add-edge")
@click.argument("source")
@click.argument("target")
@click.option("--type", "edge_type", default="DEPENDS_ON", help="Edge type")
def graph_add_edge(source: str, target: str, edge_type: str):
    """Add an edge between nodes"""
    graph_path = Path(".frctl/graph.json")
    
    if not graph_path.exists():
        click.echo("No graph found. Run 'frctl graph init' first.")
        return
    
    # Validate edge type
    try:
        etype = EdgeType(edge_type)
    except ValueError:
        click.echo(f"Invalid edge type: {edge_type}")
        click.echo(f"Valid types: {', '.join([t.value for t in EdgeType])}")
        return
    
    g = FederatedGraph.load(graph_path)
    
    try:
        edge = Edge(source=source, target=target, edge_type=etype)
        g.add_edge(edge)
        g.save(graph_path)
        click.echo(f"✓ Added edge: {source} --[{edge_type}]--> {target}")
    except Exception as e:
        click.echo(f"Error: {e}")


@graph.command("remove-node")
@click.argument("node_id")
def graph_remove_node(node_id: str):
    """Remove a node from the graph"""
    graph_path = Path(".frctl/graph.json")
    
    if not graph_path.exists():
        click.echo("No graph found. Run 'frctl graph init' first.")
        return
    
    g = FederatedGraph.load(graph_path)
    
    try:
        g.remove_node(node_id)
        g.save(graph_path)
        click.echo(f"✓ Removed node: {node_id}")
    except Exception as e:
        click.echo(f"Error: {e}")


@graph.command("remove-edge")
@click.argument("source")
@click.argument("target")
def graph_remove_edge(source: str, target: str):
    """Remove an edge from the graph"""
    graph_path = Path(".frctl/graph.json")
    
    if not graph_path.exists():
        click.echo("No graph found. Run 'frctl graph init' first.")
        return
    
    g = FederatedGraph.load(graph_path)
    g.remove_edge(source, target)
    g.save(graph_path)
    
    click.echo(f"✓ Removed edge: {source} --> {target}")


@graph.command("validate")
def graph_validate():
    """Validate graph integrity"""
    graph_path = Path(".frctl/graph.json")
    
    if not graph_path.exists():
        click.echo("No graph found. Run 'frctl graph init' first.")
        return
    
    g = FederatedGraph.load(graph_path)
    errors = g.validate()
    
    if not errors:
        click.echo("✓ Graph is valid")
    else:
        click.echo("✗ Graph has validation errors:")
        for error in errors:
            click.echo(f"  - {error}")
        raise SystemExit(1)


@graph.command("export")
@click.argument("output", type=click.Path(), required=False)
def graph_export(output: str):
    """Export graph as JSON"""
    graph_path = Path(".frctl/graph.json")
    
    if not graph_path.exists():
        click.echo("No graph found. Run 'frctl graph init' first.")
        return
    
    g = FederatedGraph.load(graph_path)
    
    if output:
        g.save(Path(output))
        click.echo(f"✓ Exported graph to {output}")
    else:
        import json
        click.echo(json.dumps(g.to_dict(), indent=2))


@graph.command("stats")
def graph_stats():
    """Show graph statistics"""
    graph_path = Path(".frctl/graph.json")
    
    if not graph_path.exists():
        click.echo("No graph found. Run 'frctl graph init' first.")
        return
    
    g = FederatedGraph.load(graph_path)
    
    click.echo("Graph Statistics:")
    click.echo(f"  Total Nodes: {g.node_count()}")
    click.echo(f"  Total Edges: {g.edge_count()}")
    click.echo(f"  Max Depth:   {g.depth()}")
    click.echo(f"  Merkle Hash: {g.merkle_hash()}")
    
    # Count by node type
    type_counts = {}
    for node in g.nodes.values():
        type_counts[node.type.value] = type_counts.get(node.type.value, 0) + 1
    
    if type_counts:
        click.echo("\n  Nodes by Type:")
        for ntype, count in sorted(type_counts.items()):
            click.echo(f"    {ntype:10} {count}")


@plan.command("init")
@click.argument("description")
@click.option("--model", default=None, help="LLM model to use")
def plan_init(description: str, model: str):
    """Start a new planning session"""
    click.echo(f"\n🎯 Initializing planning session...")
    click.echo(f"   Goal: {description}")
    if model:
        click.echo(f"   Model: {model}")
    click.echo()
    
    try:
        # Get LLM provider
        llm = get_provider(model=model)
        
        # Create planning engine
        engine = PlanningEngine(llm_provider=llm)
        
        # Run planning
        plan_obj = engine.run(description)
        
        # Save plan (basic implementation)
        plans_dir = Path(".frctl/plans")
        plans_dir.mkdir(parents=True, exist_ok=True)
        
        plan_path = plans_dir / f"{plan_obj.id}.json"
        with open(plan_path, 'w') as f:
            f.write(plan_obj.model_dump_json(indent=2))
        
        click.echo(f"\n💾 Plan saved to: {plan_path}")
        
        # Show statistics
        stats = plan_obj.get_statistics()
        click.echo(f"\n📊 Statistics:")
        click.echo(f"   Total goals: {stats['total_goals']}")
        click.echo(f"   Atomic goals: {stats['atomic_goals']}")
        click.echo(f"   Max depth: {stats['max_depth']}")
        click.echo(f"   Total tokens: {stats['total_tokens']}")
        
        # Show LLM statistics
        llm_stats = llm.get_statistics()
        click.echo(f"\n💰 LLM Usage:")
        click.echo(f"   API calls: {llm_stats['call_count']}")
        click.echo(f"   Total tokens: {llm_stats['total_tokens']}")
        click.echo(f"   Estimated cost: ${llm_stats['total_cost']}")
        
    except Exception as e:
        click.echo(f"\n❌ Planning failed: {e}", err=True)
        raise SystemExit(1)


@plan.command("list")
@click.option("--status", type=click.Choice(["in_progress", "complete", "failed"]), help="Filter by status")
def plan_list(status: str):
    """List all planning sessions"""
    from frctl.planning.persistence import PlanStore
    
    store = PlanStore()
    plans = store.list_plans(status=status)
    
    if not plans:
        click.echo("No plans found.")
        if status:
            click.echo(f"  (filtered by status: {status})")
        return
    
    click.echo(f"\n📋 Plans ({len(plans)}):")
    if status:
        click.echo(f"   Filtered by: {status}")
    click.echo()
    
    for plan_meta in plans:
        status_icon = {
            "in_progress": "⏳",
            "complete": "✅",
            "failed": "❌",
        }.get(plan_meta["status"], "❓")
        
        click.echo(f"  {status_icon} {plan_meta['id']}")
        click.echo(f"     Goal: {plan_meta['description']}")
        click.echo(f"     Status: {plan_meta['status']}")
        click.echo(f"     Created: {plan_meta['created_at']}")
        click.echo(f"     Depth: {plan_meta['max_depth']}, Goals: {plan_meta['goal_count']}")
        click.echo()


@plan.command("status")
@click.argument("plan_id", required=False)
def plan_status(plan_id: str):
    """Show planning tree structure"""
    from frctl.planning.persistence import PlanStore
    
    store = PlanStore()
    
    # If no plan_id, try to find most recent
    if not plan_id:
        plans = store.list_plans(status="in_progress")
        if not plans:
            click.echo("No in-progress plans found. Use: frctl plan list")
            return
        plan_id = plans[0]["id"]
        click.echo(f"Using most recent plan: {plan_id}\n")
    
    # Load plan
    plan = store.load(plan_id)
    if not plan:
        click.echo(f"Plan '{plan_id}' not found.")
        return
    
    # Show header
    root_goal = plan.get_goal(plan.root_goal_id)
    click.echo(f"\n📊 Plan: {plan.id}")
    click.echo(f"   Goal: {root_goal.description}")
    click.echo(f"   Status: {plan.status}")
    click.echo(f"   Created: {plan.created_at.strftime('%Y-%m-%d %H:%M')}")
    click.echo()
    
    # Show tree
    def print_goal_tree(goal, plan, indent=0):
        """Recursively print goal tree"""
        prefix = "  " * indent
        
        # Status icon
        status_icon = {
            "pending": "⏸️",
            "decomposing": "🔄",
            "atomic": "✅",
            "complete": "✅",
            "failed": "❌",
        }.get(goal.status.value, "❓")
        
        # Print goal
        click.echo(f"{prefix}{status_icon} {goal.id}")
        click.echo(f"{prefix}   {goal.description[:60]}...")
        
        # Print digest if available
        if goal.digest:
            click.echo(f"{prefix}   💭 {goal.digest[:50]}...")
        
        # Print children
        for child_id in goal.child_ids:
            child = plan.get_goal(child_id)
            if child:
                print_goal_tree(child, plan, indent + 1)
    
    click.echo("Goal Tree:")
    print_goal_tree(root_goal, plan)
    
    # Show statistics
    stats = plan.get_statistics()
    click.echo(f"\n📈 Statistics:")
    click.echo(f"   Total goals: {stats['total_goals']}")
    click.echo(f"   Atomic goals: {stats['atomic_goals']}")
    click.echo(f"   Max depth: {stats['max_depth']}")
    click.echo(f"   Total tokens: {stats['total_tokens']}")
    click.echo(f"   Complete: {stats['is_complete']}")


@plan.command("continue")
@click.argument("plan_id", required=False)
@click.option("--model", default=None, help="LLM model to use")
def plan_continue(plan_id: str, model: str):
    """Resume planning session"""
    from frctl.planning.persistence import PlanStore
    
    store = PlanStore()
    
    # If no plan_id, try to find most recent in-progress
    if not plan_id:
        plans = store.list_plans(status="in_progress")
        if not plans:
            click.echo("No in-progress plans found.")
            return
        plan_id = plans[0]["id"]
        click.echo(f"Resuming most recent plan: {plan_id}\n")
    
    # Load plan
    plan = store.load(plan_id)
    if not plan:
        click.echo(f"Plan '{plan_id}' not found.")
        return
    
    root_goal = plan.get_goal(plan.root_goal_id)
    click.echo(f"\n🔄 Resuming planning session...")
    click.echo(f"   Plan: {plan.id}")
    click.echo(f"   Goal: {root_goal.description}")
    if model:
        click.echo(f"   Model: {model}")
    click.echo()
    
    try:
        # Get LLM provider
        from frctl.llm.provider import get_provider
        llm = get_provider(model=model)
        
        # Create planning engine and load existing plan
        engine = PlanningEngine(llm_provider=llm)
        
        # Continue planning (this would need engine.continue_planning method)
        click.echo("⚠️  Plan continuation not yet implemented in engine")
        click.echo("   Use 'frctl plan status' to view current state")
        
    except Exception as e:
        click.echo(f"\n❌ Failed to resume: {e}", err=True)
        raise SystemExit(1)


@plan.command("review")
@click.argument("goal_id")
@click.option("--plan-id", help="Plan ID (defaults to most recent)")
def plan_review(goal_id: str, plan_id: str):
    """Review goal details"""
    from frctl.planning.persistence import PlanStore
    
    store = PlanStore()
    
    # Find plan
    if not plan_id:
        plans = store.list_plans()
        if not plans:
            click.echo("No plans found.")
            return
        plan_id = plans[0]["id"]
    
    # Load plan
    plan = store.load(plan_id)
    if not plan:
        click.echo(f"Plan '{plan_id}' not found.")
        return
    
    # Find goal
    goal = plan.get_goal(goal_id)
    if not goal:
        click.echo(f"Goal '{goal_id}' not found in plan '{plan_id}'.")
        return
    
    # Display goal details
    click.echo(f"\n🎯 Goal: {goal.id}")
    click.echo(f"   Description: {goal.description}")
    click.echo(f"   Status: {goal.status.value}")
    click.echo(f"   Depth: {goal.depth}")
    click.echo(f"   Created: {goal.created_at.strftime('%Y-%m-%d %H:%M')}")
    
    if goal.parent_id:
        parent = plan.get_goal(goal.parent_id)
        if parent:
            click.echo(f"\n👆 Parent: {goal.parent_id}")
            click.echo(f"   {parent.description[:60]}...")
    
    if goal.child_ids:
        click.echo(f"\n👇 Children ({len(goal.child_ids)}):")
        for child_id in goal.child_ids:
            child = plan.get_goal(child_id)
            if child:
                status = child.status.value
                click.echo(f"   - {child_id} ({status})")
                click.echo(f"     {child.description[:60]}...")
    
    if goal.reasoning:
        click.echo(f"\n💭 Reasoning:")
        click.echo(f"   {goal.reasoning}")
    
    if goal.digest:
        click.echo(f"\n📝 Digest:")
        click.echo(f"   {goal.digest}")
    
    if goal.dependencies:
        click.echo(f"\n🔗 Dependencies:")
        for dep in goal.dependencies:
            click.echo(f"   - {dep}")
    
    click.echo(f"\n📊 Metrics:")
    click.echo(f"   Tokens used: {goal.tokens_used}")


@plan.command("export")
@click.argument("plan_id")
@click.argument("output", type=click.Path(), required=False)
def plan_export(plan_id: str, output: str):
    """Export plan as JSON"""
    from frctl.planning.persistence import PlanStore
    import json
    
    store = PlanStore()
    plan = store.load(plan_id)
    
    if not plan:
        click.echo(f"Plan '{plan_id}' not found.")
        return
    
    plan_json = plan.model_dump_json(indent=2)
    
    if output:
        with open(output, 'w') as f:
            f.write(plan_json)
        click.echo(f"✓ Exported plan to {output}")
    else:
        click.echo(plan_json)


@plan.command("visualize")
@click.argument("plan_id")
@click.option("--format", type=click.Choice(["ascii", "mermaid"]), default="ascii", help="Output format")
def plan_visualize(plan_id: str, format: str):
    """Generate tree visualization"""
    from frctl.planning.persistence import PlanStore
    
    store = PlanStore()
    plan = store.load(plan_id)
    
    if not plan:
        click.echo(f"Plan '{plan_id}' not found.")
        return
    
    if format == "mermaid":
        # Generate Mermaid diagram
        click.echo("```mermaid")
        click.echo("graph TD")
        
        def add_node_mermaid(goal, plan):
            status_style = {
                "pending": ":::pending",
                "decomposing": ":::decomposing",
                "atomic": ":::atomic",
                "complete": ":::complete",
                "failed": ":::failed",
            }.get(goal.status.value, "")
            
            label = goal.description[:40].replace('"', "'")
            click.echo(f'    {goal.id}["{label}"]{status_style}')
            
            for child_id in goal.child_ids:
                child = plan.get_goal(child_id)
                if child:
                    click.echo(f'    {goal.id} --> {child_id}')
                    add_node_mermaid(child, plan)
        
        root = plan.get_goal(plan.root_goal_id)
        add_node_mermaid(root, plan)
        
        click.echo("    classDef atomic fill:#90EE90")
        click.echo("    classDef complete fill:#90EE90")
        click.echo("    classDef pending fill:#FFE4B5")
        click.echo("    classDef failed fill:#FFB6C1")
        click.echo("```")
    else:
        # ASCII tree
        def print_ascii_tree(goal, plan, prefix="", is_last=True):
            connector = "└── " if is_last else "├── "
            status = goal.status.value[0].upper()
            click.echo(f"{prefix}{connector}[{status}] {goal.description[:50]}")
            
            children = [plan.get_goal(cid) for cid in goal.child_ids if plan.get_goal(cid)]
            for i, child in enumerate(children):
                extension = "    " if is_last else "│   "
                print_ascii_tree(child, plan, prefix + extension, i == len(children) - 1)
        
        root = plan.get_goal(plan.root_goal_id)
        click.echo(f"\nPlan: {plan.id}")
        print_ascii_tree(root, plan)


@plan.command("delete")
@click.argument("plan_id")
@click.option("--archive/--no-archive", default=True, help="Archive before deleting")
@click.option("--force", is_flag=True, help="Skip confirmation")
def plan_delete(plan_id: str, archive: bool, force: bool):
    """Delete a plan"""
    from frctl.planning.persistence import PlanStore
    
    store = PlanStore()
    
    # Check if plan exists
    plan = store.load(plan_id)
    if not plan:
        click.echo(f"Plan '{plan_id}' not found.")
        return
    
    # Confirm deletion
    if not force:
        root_goal = plan.get_goal(plan.root_goal_id)
        click.echo(f"\nPlan: {plan.id}")
        click.echo(f"Goal: {root_goal.description}")
        click.echo(f"Status: {plan.status}")
        
        if archive:
            click.echo("\n⚠️  This will archive and delete the plan.")
        else:
            click.echo("\n⚠️  This will permanently delete the plan (no archive).")
        
        if not click.confirm("Continue?"):
            click.echo("Cancelled.")
            return
    
    # Delete
    try:
        success = store.delete(plan_id, archive=archive)
        if success:
            if archive:
                click.echo(f"✓ Plan archived and deleted: {plan_id}")
            else:
                click.echo(f"✓ Plan deleted: {plan_id}")
        else:
            click.echo(f"❌ Failed to delete plan: {plan_id}")
            raise SystemExit(1)
    except Exception as e:
        click.echo(f"❌ Error deleting plan: {e}", err=True)
        raise SystemExit(1)


@cli.group()
def config():
    """Manage frctl configuration"""
    pass


@config.command("init")
@click.option("--global", "is_global", is_flag=True, help="Create global config (~/.frctl/)")
@click.option("--force", is_flag=True, help="Overwrite existing config")
def config_init(is_global: bool, force: bool):
    """Initialize configuration file"""
    from frctl.config import FrctlConfig
    from pathlib import Path
    import shutil
    
    # Determine target path
    if is_global:
        config_path = Path.home() / ".frctl" / "config.toml"
    else:
        config_path = Path.cwd() / ".frctl" / "config.toml"
    
    # Check if already exists
    if config_path.exists() and not force:
        click.echo(f"Configuration already exists at {config_path}")
        click.echo("Use --force to overwrite.")
        return
    
    # Copy template
    template_path = Path(__file__).parent / "config_template.toml"
    config_path.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy(template_path, config_path)
    
    click.echo(f"✓ Created configuration at {config_path}")
    click.echo(f"\nEdit the file to configure:")
    click.echo(f"  - LLM provider and model")
    click.echo(f"  - Planning preferences")
    click.echo(f"\nOr set environment variables:")
    click.echo(f"  - FRCTL_LLM_MODEL=gpt-4")
    click.echo(f"  - OPENAI_API_KEY=sk-...")


@config.command("show")
@click.option("--all", "show_all", is_flag=True, help="Show all config sources")
def config_show(show_all: bool):
    """Display current configuration"""
    from frctl.config import get_config
    from pathlib import Path
    import json
    
    try:
        config = get_config()
        
        click.echo("\n📋 Current Configuration\n")
        
        click.echo("🤖 LLM Settings:")
        click.echo(f"   Model:       {config.llm.model}")
        click.echo(f"   Temperature: {config.llm.temperature}")
        click.echo(f"   Max Tokens:  {config.llm.max_tokens}")
        click.echo(f"   Retries:     {config.llm.num_retries}")
        click.echo(f"   Verbose:     {config.llm.verbose}")
        if config.llm.fallback_models:
            click.echo(f"   Fallbacks:   {', '.join(config.llm.fallback_models)}")
        
        click.echo("\n📐 Planning Settings:")
        click.echo(f"   Max Depth:         {config.planning.max_depth}")
        click.echo(f"   Auto Decompose:    {config.planning.auto_decompose}")
        click.echo(f"   Context Window:    {config.planning.context_window_size:,} tokens")
        
        if show_all:
            click.echo("\n📁 Config Sources:")
            user_config = Path.home() / ".frctl" / "config.toml"
            project_config = Path.cwd() / ".frctl" / "config.toml"
            
            if user_config.exists():
                click.echo(f"   ✓ User:    {user_config}")
            else:
                click.echo(f"   ✗ User:    {user_config} (not found)")
            
            if project_config.exists():
                click.echo(f"   ✓ Project: {project_config}")
            else:
                click.echo(f"   ✗ Project: {project_config} (not found)")
            
            click.echo(f"\n   Environment overrides active: {any([
                os.getenv('FRCTL_LLM_MODEL'),
                os.getenv('FRCTL_LLM_TEMPERATURE'),
                os.getenv('FRCTL_LLM_MAX_TOKENS'),
            ])}")
        
        click.echo()
        
    except Exception as e:
        click.echo(f"❌ Error loading configuration: {e}", err=True)
        raise SystemExit(1)


@config.command("validate")
def config_validate():
    """Validate configuration"""
    from frctl.config import get_config, ConfigurationError
    
    try:
        config = get_config()
        config.validate()
        click.echo("✓ Configuration is valid")
    except ConfigurationError as e:
        click.echo(f"❌ Configuration error: {e}", err=True)
        raise SystemExit(1)
    except Exception as e:
        click.echo(f"❌ Error validating configuration: {e}", err=True)
        raise SystemExit(1)


@config.command("test")
@click.option("--model", help="Override model for test")
def config_test(model: str):
    """Test LLM provider configuration"""
    from frctl.llm.provider import get_provider
    
    try:
        click.echo("🔌 Testing LLM provider connection...\n")
        
        provider = get_provider(model=model)
        click.echo(f"Model: {provider.model}")
        click.echo(f"Testing with simple prompt...\n")
        
        response = provider.generate([
            {"role": "user", "content": "Say 'Configuration test successful!' and nothing else."}
        ])
        
        click.echo(f"✓ Response: {response['content']}")
        click.echo(f"✓ Tokens: {response['usage']['total_tokens']}")
        click.echo(f"✓ Cost: ${response['cost']:.4f}")
        click.echo("\n✅ Provider connection successful!")
        
    except Exception as e:
        click.echo(f"\n❌ Provider test failed: {e}", err=True)
        click.echo("\nTroubleshooting:")
        click.echo("  1. Check API key is set (e.g., OPENAI_API_KEY)")
        click.echo("  2. Verify model name is correct")
        click.echo("  3. Check network connectivity")
        raise SystemExit(1)


# Delete duplicate section below
@cli.command()
def hello():
    """Display a hello world message"""
    click.echo("Hello from frctl!")


if __name__ == "__main__":
    cli()

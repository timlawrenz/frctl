"""Main entry point for the frctl CLI."""
import click
from pathlib import Path

from frctl.graph import FederatedGraph, Node, NodeType, Edge, EdgeType
from frctl.graph.dag import generate_purl


@click.group()
def cli():
    """frctl - Fractal project management tool"""
    pass


@cli.group()
def graph():
    """Manage the architectural graph"""
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


@cli.command()
def hello():
    """Display a hello world message"""
    click.echo("Hello from frctl!")


if __name__ == "__main__":
    cli()

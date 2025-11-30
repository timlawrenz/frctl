"""
Example: Building a Microservices Architecture Graph

This example demonstrates how to model a typical microservices
architecture using the Federated Graph.
"""

from frctl.graph import FederatedGraph, Node, NodeType, Edge, EdgeType
from frctl.graph.dag import generate_purl
from pathlib import Path


def build_microservices_graph():
    """Build a complete microservices architecture graph."""
    
    # Create the graph
    g = FederatedGraph()
    g.metadata = {
        "version": "1.0",
        "environment": "production",
        "organization": "acme-corp"
    }
    
    # -------------------------
    # Layer 1: Infrastructure
    # -------------------------
    
    event_bus = Node(
        id=generate_purl("event-bus"),
        type=NodeType.COMPONENT,
        name="event-bus",
        metadata={"provider": "kafka", "cluster": "prod-kafka"}
    )
    g.add_node(event_bus)
    
    cache = Node(
        id=generate_purl("cache"),
        type=NodeType.COMPONENT,
        name="cache",
        metadata={"provider": "redis", "cluster": "prod-redis"}
    )
    g.add_node(cache)
    
    # -------------------------
    # Layer 2: Schemas
    # -------------------------
    
    user_schema = Node(
        id=generate_purl("user-schema"),
        type=NodeType.SCHEMA,
        name="user-schema",
        metadata={"version": "2.0"}
    )
    g.add_node(user_schema)
    
    order_schema = Node(
        id=generate_purl("order-schema"),
        type=NodeType.SCHEMA,
        name="order-schema",
        metadata={"version": "3.1"}
    )
    g.add_node(order_schema)
    
    order_events = Node(
        id=generate_purl("order-events"),
        type=NodeType.SCHEMA,
        name="order-events",
        metadata={"version": "1.5"}
    )
    g.add_node(order_events)
    
    # -------------------------
    # Layer 3: Shared Libraries
    # -------------------------
    
    auth_utils = Node(
        id=generate_purl("auth-utils"),
        type=NodeType.LIBRARY,
        name="auth-utils",
        metadata={"language": "python", "version": "1.2.0"}
    )
    g.add_node(auth_utils)
    
    logging_lib = Node(
        id=generate_purl("logging-lib"),
        type=NodeType.LIBRARY,
        name="logging-lib",
        metadata={"language": "python", "version": "2.0.1"}
    )
    g.add_node(logging_lib)
    
    # -------------------------
    # Layer 4: Core Services
    # -------------------------
    
    user_service = Node(
        id=generate_purl("user-service"),
        type=NodeType.SERVICE,
        name="user-service",
        metadata={
            "team": "users",
            "language": "python",
            "database": "postgres"
        }
    )
    g.add_node(user_service)
    
    order_service = Node(
        id=generate_purl("order-service"),
        type=NodeType.SERVICE,
        name="order-service",
        metadata={
            "team": "commerce",
            "language": "python",
            "database": "postgres"
        }
    )
    g.add_node(order_service)
    
    payment_service = Node(
        id=generate_purl("payment-service"),
        type=NodeType.SERVICE,
        name="payment-service",
        metadata={
            "team": "payments",
            "language": "java",
            "database": "postgres"
        }
    )
    g.add_node(payment_service)
    
    notification_service = Node(
        id=generate_purl("notification-service"),
        type=NodeType.SERVICE,
        name="notification-service",
        metadata={
            "team": "platform",
            "language": "go"
        }
    )
    g.add_node(notification_service)
    
    # -------------------------
    # Layer 5: API Gateway
    # -------------------------
    
    api_gateway = Node(
        id=generate_purl("api-gateway"),
        type=NodeType.SERVICE,
        name="api-gateway",
        metadata={
            "team": "platform",
            "language": "go",
            "public_facing": True
        }
    )
    g.add_node(api_gateway)
    
    # -------------------------
    # Edges: Infrastructure Dependencies
    # -------------------------
    
    # Services depend on infrastructure
    for service in [order_service, notification_service]:
        g.add_edge(Edge(
            source=service.id,
            target=event_bus.id,
            edge_type=EdgeType.DEPENDS_ON
        ))
    
    # User service uses cache
    g.add_edge(Edge(
        source=user_service.id,
        target=cache.id,
        edge_type=EdgeType.DEPENDS_ON
    ))
    
    # -------------------------
    # Edges: Schema Implementation
    # -------------------------
    
    # User service implements user schema
    g.add_edge(Edge(
        source=user_service.id,
        target=user_schema.id,
        edge_type=EdgeType.IMPLEMENTS,
        contract="contracts/user-schema.tsp"
    ))
    
    # Order service owns order schema
    g.add_edge(Edge(
        source=order_service.id,
        target=order_schema.id,
        edge_type=EdgeType.OWNS,
        contract="contracts/order-schema.tsp"
    ))
    
    # Order service owns order events
    g.add_edge(Edge(
        source=order_service.id,
        target=order_events.id,
        edge_type=EdgeType.OWNS,
        contract="contracts/order-events.tsp"
    ))
    
    # -------------------------
    # Edges: Library Dependencies
    # -------------------------
    
    # All Python services use auth utils
    for service in [user_service, order_service]:
        g.add_edge(Edge(
            source=service.id,
            target=auth_utils.id,
            edge_type=EdgeType.DEPENDS_ON
        ))
    
    # All services use logging
    for service in [user_service, order_service, payment_service, notification_service]:
        g.add_edge(Edge(
            source=service.id,
            target=logging_lib.id,
            edge_type=EdgeType.DEPENDS_ON
        ))
    
    # -------------------------
    # Edges: Service Dependencies
    # -------------------------
    
    # API Gateway depends on core services
    for service in [user_service, order_service, payment_service]:
        g.add_edge(Edge(
            source=api_gateway.id,
            target=service.id,
            edge_type=EdgeType.DEPENDS_ON
        ))
    
    # Order service depends on user service
    g.add_edge(Edge(
        source=order_service.id,
        target=user_service.id,
        edge_type=EdgeType.DEPENDS_ON
    ))
    
    # Order service depends on payment service
    g.add_edge(Edge(
        source=order_service.id,
        target=payment_service.id,
        edge_type=EdgeType.DEPENDS_ON
    ))
    
    # -------------------------
    # Edges: Event Consumption
    # -------------------------
    
    # Notification service consumes order events
    g.add_edge(Edge(
        source=notification_service.id,
        target=order_events.id,
        edge_type=EdgeType.CONSUMES,
        contract="contracts/order-events.tsp"
    ))
    
    return g


def analyze_graph(g: FederatedGraph):
    """Analyze the graph structure."""
    
    print("=" * 60)
    print("GRAPH ANALYSIS")
    print("=" * 60)
    
    # Basic statistics
    print(f"\nStatistics:")
    print(f"  Total Nodes: {g.node_count()}")
    print(f"  Total Edges: {g.edge_count()}")
    print(f"  Max Depth:   {g.depth()}")
    print(f"  Merkle Hash: {g.merkle_hash()[:16]}...")
    
    # Count by type
    type_counts = {}
    for node in g.nodes.values():
        type_counts[node.type.value] = type_counts.get(node.type.value, 0) + 1
    
    print(f"\nNodes by Type:")
    for ntype, count in sorted(type_counts.items()):
        print(f"  {ntype:12} {count:2}")
    
    # Topological sort (build order)
    print(f"\nBuild Order (topological sort):")
    sorted_nodes = g.topological_sort()
    for i, node_id in enumerate(sorted_nodes, 1):
        node = g.get_node(node_id)
        print(f"  {i:2}. {node.type.value:12} {node.name}")
    
    # Find critical nodes (most dependencies)
    print(f"\nMost Depended-On Nodes:")
    dep_counts = {}
    for edge in g.edges:
        dep_counts[edge.target] = dep_counts.get(edge.target, 0) + 1
    
    for node_id, count in sorted(dep_counts.items(), key=lambda x: x[1], reverse=True)[:5]:
        node = g.get_node(node_id)
        print(f"  {node.name:25} {count} dependents")
    
    # Validate
    errors = g.validate()
    print(f"\nValidation: {'✓ PASSED' if not errors else '✗ FAILED'}")
    if errors:
        for error in errors:
            print(f"  - {error}")


def main():
    """Main entry point."""
    
    print("Building microservices architecture graph...\n")
    
    # Build the graph
    g = build_microservices_graph()
    
    # Analyze it
    analyze_graph(g)
    
    # Save to file
    output_path = Path(".frctl/graph.json")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    g.save(output_path)
    
    print(f"\n✓ Graph saved to {output_path}")
    
    # Example: Query specific dependencies
    print("\n" + "=" * 60)
    print("DEPENDENCY ANALYSIS")
    print("=" * 60)
    
    # What does api-gateway depend on?
    api_gateway_id = generate_purl("api-gateway")
    ancestors = g.get_ancestors(api_gateway_id)
    print(f"\napi-gateway depends on {len(ancestors)} components:")
    for node_id in ancestors[:10]:  # Show first 10
        node = g.get_node(node_id)
        print(f"  - {node.type.value:12} {node.name}")
    
    # What depends on auth-utils?
    auth_utils_id = generate_purl("auth-utils")
    descendants = g.get_descendants(auth_utils_id)
    print(f"\nauth-utils is used by {len(descendants)} components:")
    for node_id in descendants:
        node = g.get_node(node_id)
        print(f"  - {node.type.value:12} {node.name}")


if __name__ == "__main__":
    main()

# Graph JSON Schema

The Federated Graph uses a deterministic JSON format for persistence and interchange.

## Schema Definition

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "FederatedGraph",
  "description": "A Directed Acyclic Graph representing software architecture",
  "type": "object",
  "required": ["nodes", "edges", "metadata"],
  "properties": {
    "metadata": {
      "type": "object",
      "description": "Graph-level metadata",
      "additionalProperties": true
    },
    "nodes": {
      "type": "object",
      "description": "Nodes indexed by PURL identifier",
      "additionalProperties": {
        "$ref": "#/definitions/Node"
      }
    },
    "edges": {
      "type": "array",
      "description": "List of edges connecting nodes",
      "items": {
        "$ref": "#/definitions/Edge"
      }
    }
  },
  "definitions": {
    "Node": {
      "type": "object",
      "required": ["id", "type", "name", "metadata"],
      "properties": {
        "id": {
          "type": "string",
          "description": "Unique PURL identifier",
          "pattern": "^pkg:frctl/[a-z0-9-]+@local$",
          "example": "pkg:frctl/api-gateway@local"
        },
        "type": {
          "type": "string",
          "enum": ["Service", "Library", "Schema", "Endpoint", "Component"],
          "description": "Type of architectural component"
        },
        "name": {
          "type": "string",
          "description": "Human-readable name",
          "minLength": 1
        },
        "metadata": {
          "type": "object",
          "description": "Additional node metadata",
          "additionalProperties": true
        }
      }
    },
    "Edge": {
      "type": "object",
      "required": ["source", "target", "edge_type", "metadata"],
      "properties": {
        "source": {
          "type": "string",
          "description": "Source node PURL",
          "pattern": "^pkg:frctl/[a-z0-9-]+@local$"
        },
        "target": {
          "type": "string",
          "description": "Target node PURL",
          "pattern": "^pkg:frctl/[a-z0-9-]+@local$"
        },
        "edge_type": {
          "type": "string",
          "enum": ["DEPENDS_ON", "CONSUMES", "OWNS", "IMPLEMENTS"],
          "description": "Type of relationship"
        },
        "metadata": {
          "type": "object",
          "description": "Additional edge metadata",
          "additionalProperties": true
        },
        "contract": {
          "type": ["string", "null"],
          "description": "Path to TypeSpec contract file",
          "example": "contracts/api.tsp"
        }
      }
    }
  }
}
```

## Example: Empty Graph

```json
{
  "metadata": {},
  "nodes": {},
  "edges": []
}
```

## Example: Simple Graph

```json
{
  "metadata": {
    "version": "1.0",
    "created": "2024-11-30T00:00:00Z"
  },
  "nodes": {
    "pkg:frctl/api-gateway@local": {
      "id": "pkg:frctl/api-gateway@local",
      "type": "Service",
      "name": "api-gateway",
      "metadata": {
        "version": "1.2.3",
        "team": "platform"
      }
    },
    "pkg:frctl/auth-utils@local": {
      "id": "pkg:frctl/auth-utils@local",
      "type": "Library",
      "name": "auth-utils",
      "metadata": {
        "version": "2.0.0"
      }
    }
  },
  "edges": [
    {
      "source": "pkg:frctl/api-gateway@local",
      "target": "pkg:frctl/auth-utils@local",
      "edge_type": "DEPENDS_ON",
      "metadata": {
        "version_constraint": "^2.0"
      },
      "contract": null
    }
  ]
}
```

## Example: Graph with TypeSpec Contract

```json
{
  "metadata": {},
  "nodes": {
    "pkg:frctl/payment-service@local": {
      "id": "pkg:frctl/payment-service@local",
      "type": "Service",
      "name": "payment-service",
      "metadata": {}
    },
    "pkg:frctl/payment-api@local": {
      "id": "pkg:frctl/payment-api@local",
      "type": "Schema",
      "name": "payment-api",
      "metadata": {}
    }
  },
  "edges": [
    {
      "source": "pkg:frctl/payment-service@local",
      "target": "pkg:frctl/payment-api@local",
      "edge_type": "IMPLEMENTS",
      "metadata": {},
      "contract": "contracts/payment-api.tsp"
    }
  ]
}
```

## Example: Complex Architecture

```json
{
  "metadata": {
    "version": "2.0",
    "environment": "production"
  },
  "nodes": {
    "pkg:frctl/api-gateway@local": {
      "id": "pkg:frctl/api-gateway@local",
      "type": "Service",
      "name": "api-gateway",
      "metadata": {
        "team": "platform",
        "repo": "https://github.com/org/api-gateway"
      }
    },
    "pkg:frctl/user-service@local": {
      "id": "pkg:frctl/user-service@local",
      "type": "Service",
      "name": "user-service",
      "metadata": {
        "team": "users",
        "database": "postgres"
      }
    },
    "pkg:frctl/order-service@local": {
      "id": "pkg:frctl/order-service@local",
      "type": "Service",
      "name": "order-service",
      "metadata": {
        "team": "commerce"
      }
    },
    "pkg:frctl/event-bus@local": {
      "id": "pkg:frctl/event-bus@local",
      "type": "Component",
      "name": "event-bus",
      "metadata": {
        "provider": "kafka"
      }
    },
    "pkg:frctl/order-events@local": {
      "id": "pkg:frctl/order-events@local",
      "type": "Schema",
      "name": "order-events",
      "metadata": {}
    }
  },
  "edges": [
    {
      "source": "pkg:frctl/api-gateway@local",
      "target": "pkg:frctl/user-service@local",
      "edge_type": "DEPENDS_ON",
      "metadata": {},
      "contract": null
    },
    {
      "source": "pkg:frctl/api-gateway@local",
      "target": "pkg:frctl/order-service@local",
      "edge_type": "DEPENDS_ON",
      "metadata": {},
      "contract": null
    },
    {
      "source": "pkg:frctl/order-service@local",
      "target": "pkg:frctl/event-bus@local",
      "edge_type": "DEPENDS_ON",
      "metadata": {},
      "contract": null
    },
    {
      "source": "pkg:frctl/order-service@local",
      "target": "pkg:frctl/order-events@local",
      "edge_type": "OWNS",
      "metadata": {},
      "contract": "contracts/order-events.tsp"
    },
    {
      "source": "pkg:frctl/user-service@local",
      "target": "pkg:frctl/order-events@local",
      "edge_type": "CONSUMES",
      "metadata": {},
      "contract": "contracts/order-events.tsp"
    }
  ]
}
```

## Key Features

### Deterministic Serialization

The JSON format uses deterministic serialization to ensure:

1. **Alphabetically sorted keys** - Node IDs and metadata keys are sorted
2. **Stable edge ordering** - Edges are sorted by (source, target)
3. **Consistent formatting** - 2-space indentation, sorted keys

This ensures the same graph always produces the same JSON, enabling:

- **Merkle hashing** for architecture fingerprinting
- **Git-friendly diffs** for version control
- **Reliable comparison** across systems

### PURL Identifiers

Nodes use [Package URL (PURL)](https://github.com/package-url/purl-spec) format:

```
pkg:frctl/<name>@local
```

Where:
- `pkg:` - PURL scheme
- `frctl` - Package type (our namespace)
- `<name>` - Sanitized node name (lowercase, hyphens)
- `@local` - Version qualifier (always "local" for now)

Examples:
- `pkg:frctl/api-gateway@local`
- `pkg:frctl/my-service@local`
- `pkg:frctl/user-schema@local`

### Validation Rules

1. **DAG Property**: Must not contain cycles
2. **Node References**: All edges must reference existing nodes
3. **Unique IDs**: Node IDs must be unique within the graph
4. **Valid Types**: Node and edge types must be from allowed enums
5. **Non-empty Names**: Node names cannot be empty or whitespace-only

## Migration Notes

When loading graphs from older formats:

### Version 1.0 → 2.0

No breaking changes. All 1.0 graphs are valid 2.0 graphs.

### Future Versions

The schema may evolve to support:

- **Remote PURLs**: `pkg:frctl/service@github/org/repo`
- **Version constraints**: Semantic versioning in edges
- **Namespaces**: Multi-tenant graph support
- **Extensions**: Plugin-specific metadata schemas

The core schema will remain backward compatible.

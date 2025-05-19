# Knowledge Base Documentation

This document provides a comprehensive overview of the knowledge base system in the AI-Driven Penetration Testing Framework.

## Table of Contents
- [Overview](#overview)
- [Architecture](#architecture)
- [Collections](#collections)
- [Vector Embeddings](#vector-embeddings)
- [Query Capabilities](#query-capabilities)
- [Data Importers](#data-importers)
- [Integration with Agents](#integration-with-agents)
- [Implementation Details](#implementation-details)
- [Extending the Knowledge Base](#extending-the-knowledge-base)
- [Performance Considerations](#performance-considerations)
- [Current Limitations](#current-limitations)

## Overview

The knowledge base serves as the security intelligence center of the framework, providing contextual information about attack patterns, vulnerabilities, service fingerprints, and security best practices. It uses vector embeddings and similarity search to find relevant security information, enabling agents to make intelligent decisions based on security knowledge.

Key features of the knowledge base include:
- **Semantic Search**: Finding relevant information based on meaning, not just keywords
- **Structured Security Data**: Organized collections of security information
- **Vector Embeddings**: Mathematical representations of security concepts
- **Context-Aware Queries**: Finding information that matches the current security context
- **Metadata Filtering**: Narrowing searches based on specific attributes

## Architecture

The knowledge base is built on ChromaDB, a vector database designed for similarity search. It uses the following components:

1. **Base Knowledge Base**: Provides fundamental vector database operations (add, query, update, delete)
2. **Security Knowledge Base**: Extends the base with security-specific collections and methods
3. **Data Importers**: Populate the knowledge base with security information
4. **Query Interface**: Allows agents to search for relevant information
5. **Embedding Model**: Converts text into vector representations for similarity search

The knowledge base is accessed through a dedicated Knowledge Base Agent, which processes queries from other agents and returns relevant information.

## Collections

The security knowledge base maintains several specialized collections:

### 1. Attack Patterns

Contains information about common attack techniques based on the MITRE ATT&CK framework.

**Key Fields**:
- **Pattern ID**: Unique identifier for the attack pattern
- **Name**: Short name of the attack technique
- **Description**: Detailed description of how the attack works
- **MITRE ID**: Reference to MITRE ATT&CK ID (e.g., T1110.003)
- **Tactics**: List of tactics this pattern belongs to (e.g., "Credential Access")
- **Techniques**: List of techniques this pattern implements

**Example Query**: "Find attack patterns related to password spraying"

### 2. Vulnerabilities

Contains information about security vulnerabilities, including CVEs and security weaknesses.

**Key Fields**:
- **Vulnerability ID**: Unique identifier for the vulnerability
- **Name**: Short name/title of the vulnerability
- **Description**: Detailed description of the vulnerability
- **CVE ID**: Common Vulnerabilities and Exposures identifier
- **CVSS Score**: Common Vulnerability Scoring System score (0-10)
- **Affected Services**: List of services affected by this vulnerability
- **Attack Vectors**: List of methods used to exploit this vulnerability

**Example Query**: "Find vulnerabilities affecting Apache 2.4.41"

### 3. Service Fingerprints

Contains information about identifying characteristics of services and applications.

**Key Fields**:
- **Fingerprint ID**: Unique identifier for the fingerprint
- **Service Name**: Name of the service
- **Version Pattern**: Regular expression pattern to match version strings
- **Description**: Detailed description of the service
- **Default Ports**: List of ports this service typically runs on
- **Banner Patterns**: Patterns typically found in service banners

**Example Query**: "Find service fingerprints for OpenSSH"

### 4. Exploits (Planned)

Will contain information about exploitation techniques for vulnerabilities.

### 5. Mitigations (Planned)

Will contain information about security controls and remediation strategies.

## Vector Embeddings

The knowledge base uses vector embeddings to represent security information in a high-dimensional space, allowing for semantic similarity search.

### Embedding Generation

1. Security information is converted into text (e.g., vulnerability descriptions)
2. The embedding model (Sentence Transformers) converts text into vector representations
3. These vectors capture the semantic meaning of the text
4. Similar concepts have vectors that are close to each other in vector space

### Similarity Search

When querying:
1. The query text is converted into a vector using the same embedding model
2. ChromaDB finds vectors in the database that are closest to the query vector
3. The corresponding documents are returned as search results
4. Results are ranked by similarity (cosine distance)

## Query Capabilities

The knowledge base provides several specialized query methods:

### 1. Attack Pattern Queries

```python
results = kb.query_attack_patterns(
    query_text="password brute force",
    n_results=5,
    tactics=["Credential Access"]
)
```

### 2. Vulnerability Queries

```python
results = kb.query_vulnerabilities(
    query_text="remote code execution in apache",
    n_results=5,
    affected_service="Apache HTTP Server",
    min_cvss=7.0
)
```

### 3. Service Fingerprint Queries

```python
results = kb.query_service_fingerprints(
    query_text="SSH server Ubuntu",
    n_results=5,
    service_name="OpenSSH",
    port=22
)
```

### Query Result Format

Query results include:
- **Documents**: The text content of matching items
- **Metadatas**: Structured data associated with each match
- **Distances**: Vector distances (lower means more similar)
- **IDs**: Unique identifiers for each match

## Data Importers

The knowledge base includes several data importers to populate security information:

### 1. MITRE ATT&CK Importer

Imports attack patterns from the MITRE ATT&CK framework.

**Implementation**: `src/knowledge_base/importers/mitre_importer.py`

### 2. Vulnerability Importer

Imports vulnerability information from various sources (e.g., CVE database).

**Implementation**: `src/knowledge_base/importers/vulnerability_importer.py`

### 3. Service Fingerprint Importer

Imports service fingerprint information for identifying services.

**Implementation**: `src/knowledge_base/importers/service_importer.py`

### 4. Security Data Importer

Main importer that coordinates the import of all security data types.

**Implementation**: `src/knowledge_base/importers/security_data_importer.py`

## Integration with Agents

Agents can interact with the knowledge base in two ways:

### 1. Direct Queries (Knowledge Base Agent)

Agents can send knowledge queries to the Knowledge Base Agent, which processes the queries and returns relevant information:

```python
# In an agent
query_message_id = await self.query_knowledge_base(
    query="Apache 2.4.41 vulnerability",
    collection="vulnerabilities",
    n_results=5
)
```

### 2. Knowledge-Enhanced Agents

Some agents (like the KB Reconnaissance Agent) have direct access to the knowledge base for real-time enhancement of their findings:

```python
# In KB Reconnaissance Agent
enriched_info = await self.enrich_service_info(
    service_name=service["service"],
    version=service["version"],
    port=service["port"]
)
```

## Implementation Details

### Base Knowledge Base Class

The `BaseKnowledgeBase` class provides core functionality for interacting with ChromaDB:

```python
class BaseKnowledgeBase:
    def __init__(self):
        # Initialize ChromaDB client and embedding model
        
    def create_collection(self, name: str, overwrite: bool = False):
        # Create a collection in ChromaDB
        
    def get_collection(self, name: str):
        # Get a collection by name
        
    def get_embedding(self, text: str) -> List[float]:
        # Generate vector embedding for text
        
    def add_texts(self, collection_name: str, texts: List[str], metadatas: Optional[List[Dict[str, Any]]] = None, ids: Optional[List[str]] = None):
        # Add texts with their embeddings to a collection
        
    def query_texts(self, collection_name: str, query_text: str, n_results: int = 5, where: Optional[Dict[str, Any]] = None):
        # Query collection by text similarity
        
    def delete_texts(self, collection_name: str, ids: List[str]):
        # Delete texts from collection by ID
        
    def update_text(self, collection_name: str, id: str, text: str, metadata: Optional[Dict[str, Any]] = None):
        # Update text and metadata for a document by ID
        
    def get_collection_stats(self, collection_name: str):
        # Get statistics about a collection
```

### Security Knowledge Base Class

The `SecurityKnowledgeBase` class extends the base class with security-specific collections and methods:

```python
class SecurityKnowledgeBase(BaseKnowledgeBase):
    def __init__(self):
        super().__init__()
        # Define security-specific collections
        
    def add_attack_pattern(self, pattern_id: str, name: str, description: str, mitre_id: Optional[str] = None, tactics: Optional[List[str]] = None, techniques: Optional[List[str]] = None):
        # Add attack pattern to knowledge base
        
    def add_vulnerability(self, vuln_id: str, name: str, description: str, cve_id: Optional[str] = None, cvss_score: Optional[float] = None, affected_services: Optional[List[str]] = None, attack_vectors: Optional[List[str]] = None):
        # Add vulnerability to knowledge base
        
    def add_service_fingerprint(self, fingerprint_id: str, service_name: str, version_pattern: str, description: str, default_ports: Optional[List[int]] = None, banner_patterns: Optional[List[str]] = None):
        # Add service fingerprint to knowledge base
        
    def query_attack_patterns(self, query_text: str, n_results: int = 5, tactics: Optional[List[str]] = None):
        # Query attack patterns by similarity and optional filters
        
    def query_vulnerabilities(self, query_text: str, n_results: int = 5, affected_service: Optional[str] = None, min_cvss: Optional[float] = None):
        # Query vulnerabilities by similarity and optional filters
        
    def query_service_fingerprints(self, query_text: str, n_results: int = 5, service_name: Optional[str] = None, port: Optional[int] = None):
        # Query service fingerprints by similarity and optional filters
```

## Extending the Knowledge Base

The knowledge base is designed to be extensible, allowing for new collections and capabilities:

### Adding a New Collection

1. Define the collection in the `SecurityKnowledgeBase` initialization:

```python
self.collections["new_collection"] = "security_new_collection"
self.create_collection(self.collections["new_collection"])
```

2. Add methods for adding items to the collection:

```python
def add_new_item(self, item_id: str, name: str, description: str, ...):
    metadata = {
        "item_id": item_id,
        "name": name,
        ...
    }
    
    self.add_texts(
        collection_name=self.collections["new_collection"],
        texts=[description],
        metadatas=[metadata],
        ids=[item_id]
    )
    
    return True
```

3. Add methods for querying the collection:

```python
def query_new_items(self, query_text: str, n_results: int = 5, ...):
    where = {}
    # Add filters to where clause
    
    return self.query_texts(
        collection_name=self.collections["new_collection"],
        query_text=query_text,
        n_results=n_results,
        where=where if where else None
    )
```

### Creating a New Importer

1. Create a new importer class:

```python
class NewItemImporter:
    def __init__(self, kb: SecurityKnowledgeBase):
        self.kb = kb
    
    def import_sample_data(self):
        # Sample data
        items = [
            {
                "id": str(uuid.uuid4()),
                "name": "Sample Item 1",
                "description": "Description of sample item 1",
                ...
            },
            ...
        ]
        
        # Import items
        for item in items:
            self.kb.add_new_item(
                item_id=item["id"],
                name=item["name"],
                description=item["description"],
                ...
            )
        
        print(f"Imported {len(items)} new items")
        return len(items)
```

2. Update the main security data importer:

```python
# In SecurityDataImporter.import_all_data
new_item_count = self.import_new_items()

return {
    "attack_patterns": attack_count,
    "vulnerabilities": vuln_count,
    "service_fingerprints": service_count,
    "new_items": new_item_count,
    "total": attack_count + vuln_count + service_count + new_item_count
}
```

## Performance Considerations

The knowledge base is designed for semantic search, not high-volume transaction processing. Consider these performance factors:

### 1. Vector Dimensionality

The embedding model (`all-MiniLM-L6-v2`) produces 384-dimensional vectors, balancing accuracy and performance. Larger models can produce higher-dimensional vectors with better semantic understanding but require more computational resources.

### 2. Collection Size

Performance scales with the number of vectors in each collection. For large collections (10,000+ items), consider:
- Adding more specific metadata filters to narrow searches
- Using batch processing for imports
- Implementing collection partitioning

### 3. Query Optimization

For faster queries:
- Use specific metadata filters where possible
- Limit the number of results returned
- Consider the tradeoff between search accuracy and speed

### 4. Embedding Generation

Generating embeddings is computationally intensive. For large imports:
- Use batch processing
- Consider offloading to dedicated hardware
- Cache commonly used embeddings

## Current Limitations

The current knowledge base implementation has several limitations:

### 1. Sample Data Only

The current implementation uses sample data for demonstration purposes. A production system would require integration with comprehensive security databases.

### 2. Limited Metadata Filtering

ChromaDB has limitations in filtering on array fields and complex metadata. The current implementation uses simplified filtering approaches.

### 3. No Versioning

The current implementation does not track changes to security data over time, which would be important for a production system.

### 4. Limited Data Sources

The current importers only handle sample data. A production system would need integration with official sources like NVD/CVE databases, MITRE ATT&CK API, etc.

### 5. Basic Embedding Model

The current implementation uses a smaller embedding model for efficiency. A production system might benefit from more sophisticated models.

### 6. In-Memory Storage

The current ChromaDB configuration uses in-memory storage. For production use, persistent storage with proper backup strategies would be essential.
#!/usr/bin/env python3
import asyncio
import argparse
import sys
import json
from src.knowledge_base.security_kb import SecurityKnowledgeBase

async def query_knowledge_base(query_text, collection_type, limit=5):
    """
    Query the security knowledge base.
    
    Args:
        query_text: Text to search for
        collection_type: Type of collection to search (attack, vuln, service)
        limit: Maximum number of results to return
    """
    print(f"Querying knowledge base for: {query_text}")
    print(f"Collection type: {collection_type}")
    print(f"Limit: {limit}")
    
    kb = SecurityKnowledgeBase()
    
    if collection_type == "attack":
        results = kb.query_attack_patterns(query_text, n_results=limit)
    elif collection_type == "vuln":
        results = kb.query_vulnerabilities(query_text, n_results=limit)
    elif collection_type == "service":
        results = kb.query_service_fingerprints(query_text, n_results=limit)
    else:
        print(f"Unknown collection type: {collection_type}")
        return False
    
    # Print results
    if results and results.get("documents") and len(results["documents"][0]) > 0:
        print(f"\nFound {len(results['documents'][0])} results:")
        for i, doc in enumerate(results["documents"][0]):
            print(f"\n--- Result {i+1} ---")
            print(f"Document: {doc[:200]}...")
            if i < len(results["metadatas"][0]):
                print(f"Metadata: {json.dumps(results['metadatas'][0][i], indent=2)}")
        return True
    else:
        print("No results found")
        return False

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Query the security knowledge base")
    parser.add_argument("query", help="Text to search for")
    parser.add_argument("--type", choices=["attack", "vuln", "service"], default="attack",
                        help="Type of collection to search")
    parser.add_argument("--limit", type=int, default=5, help="Maximum number of results to return")
    
    args = parser.parse_args()
    
    success = asyncio.run(query_knowledge_base(args.query, args.type, args.limit))
    sys.exit(0 if success else 1)
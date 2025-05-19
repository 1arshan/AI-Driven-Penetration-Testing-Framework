#!/usr/bin/env python3
import asyncio
import sys
from src.knowledge_base.base_kb import BaseKnowledgeBase

async def test_chromadb_connection():
    """
    Test the connection to ChromaDB.
    
    Creates a test collection, adds a document, and queries it to verify
    the connection is working properly.
    """
    print("Testing ChromaDB connection...")
    
    try:
        # Create knowledge base
        kb = BaseKnowledgeBase()
        
        # List collections
        collections = kb.client.list_collections()
        print(f"Found {len(collections)} existing collections")
        
        # Create a test collection
        test_collection = kb.create_collection("test_collection", overwrite=True)
        print(f"Created test collection: {test_collection.name}")
        
        # Add a document
        test_text = "This is a test document for ChromaDB connection verification."
        kb.add_texts(
            collection_name="test_collection",
            texts=[test_text],
            metadatas=[{"source": "test"}],
            ids=["test1"]
        )
        print("Added test document")
        
        # Query the document
        results = kb.query_texts(
            collection_name="test_collection",
            query_text="test document",
            n_results=1
        )
        
        if results and results.get("documents") and len(results["documents"][0]) > 0:
            print("Successfully queried test document!")
            print(f"Document: {results['documents'][0][0]}")
            print(f"Metadata: {results['metadatas'][0][0]}")
            print("\nChromaDB connection test successful!")
            return True
        else:
            print("Query returned no results")
            return False
    
    except Exception as e:
        print(f"Error testing ChromaDB connection: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_chromadb_connection())
    sys.exit(0 if success else 1)
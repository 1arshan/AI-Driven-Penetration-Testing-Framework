import os
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
from typing import Dict, List, Optional, Any
from src.utils.config import Config

class BaseKnowledgeBase:
    """
    Base class for vector database interactions.
    
    This class provides foundational functionality for storing and retrieving
    information using vector embeddings in ChromaDB.
    """
    
    def __init__(self):
        """
        Initialize the knowledge base with ChromaDB connection and embedding model.
        """
        # Connect to ChromaDB
        self.client = chromadb.HttpClient(
            host=Config.CHROMA_HOST,
            port=Config.CHROMA_PORT
        )
        
        # Initialize embedding model
        # Using a small model for development, can replace with larger one later
        self.embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
    
    def create_collection(self, name: str, overwrite: bool = False):
        """
        Create a collection in ChromaDB.
        
        A collection is a namespace for a set of documents and their embeddings.
        
        Args:
            name: Name of the collection to create
            overwrite: If True, delete existing collection with same name
            
        Returns: Collection object
        """
        try:
            # Check if collection exists
            collections = self.client.list_collections()
            collection_names = [c.name for c in collections]
            
            if name in collection_names:
                if overwrite:
                    self.client.delete_collection(name)
                else:
                    return self.client.get_collection(name)
            
            # Create new collection
            return self.client.create_collection(name)
        except Exception as e:
            print(f"Error creating collection: {e}")
            raise
    
    def get_collection(self, name: str):
        """
        Get a collection by name.
        
        Args:
            name: Name of the collection to retrieve
            
        Returns: Collection object if exists, None otherwise
        """
        try:
            return self.client.get_collection(name)
        except Exception as e:
            print(f"Error getting collection: {e}")
            return None
    
    def get_embedding(self, text: str) -> List[float]:
        """
        Generate embedding vector for text.
        
        Converts text into a numerical vector representation using the
        sentence transformer model.
        
        Args:
            text: Text to encode as a vector
            
        Returns: List of floats representing the text embedding
        """
        return self.embedding_model.encode(text).tolist()
    
    def add_texts(
        self,
        collection_name: str,
        texts: List[str],
        metadatas: Optional[List[Dict[str, Any]]] = None,
        ids: Optional[List[str]] = None
    ):
        """
        Add texts with their embeddings to a collection.
        
        Args:
            collection_name: Name of the collection
            texts: List of text documents to add
            metadatas: Optional list of metadata dictionaries for each text
            ids: Optional list of unique IDs for each text
            
        Returns: None
        """
        collection = self.get_collection(collection_name)
        if not collection:
            collection = self.create_collection(collection_name)
        
        # Generate embeddings
        embeddings = [self.get_embedding(text) for text in texts]
        
        # Add to collection
        collection.add(
            embeddings=embeddings,
            documents=texts,
            metadatas=metadatas or [{} for _ in texts],
            ids=ids or [f"doc_{i}" for i in range(len(texts))]
        )
    
    def query_texts(
        self,
        collection_name: str,
        query_text: str,
        n_results: int = 5,
        where: Optional[Dict[str, Any]] = None
    ):
        """
        Query collection by text similarity.
        
        Finds texts in the collection that are semantically similar to the query.
        
        Args:
            collection_name: Name of the collection to search
            query_text: Text to find similar documents for
            n_results: Maximum number of results to return
            where: Optional filter conditions for metadata
            
        Returns: Dictionary with query results
        """
        collection = self.get_collection(collection_name)
        if not collection:
            return {"matches": []}
        
        # Generate query embedding
        query_embedding = self.get_embedding(query_text)
        
        # Query collection
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results,
            where=where
        )
        
        return results
    
    def delete_texts(
        self,
        collection_name: str,
        ids: List[str]
    ):
        """
        Delete texts from collection by ID.
        
        Args:
            collection_name: Name of the collection
            ids: List of document IDs to delete
            
        Returns: True if successful, False otherwise
        """
        collection = self.get_collection(collection_name)
        if not collection:
            return False
        
        collection.delete(ids=ids)
        return True
    
    def update_text(
        self,
        collection_name: str,
        id: str,
        text: str,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Update text and metadata for a document by ID.
        
        Args:
            collection_name: Name of the collection
            id: ID of the document to update
            text: New text content
            metadata: New metadata dictionary
            
        Returns: True if successful, False otherwise
        """
        collection = self.get_collection(collection_name)
        if not collection:
            return False
        
        # Generate embedding
        embedding = self.get_embedding(text)
        
        # Update in collection
        collection.update(
            ids=[id],
            embeddings=[embedding],
            documents=[text],
            metadatas=[metadata or {}]
        )
        
        return True
    
    def get_collection_stats(self, collection_name: str):
        """
        Get statistics about a collection.
        
        Args:
            collection_name: Name of the collection
            
        Returns: Dictionary with collection statistics
        """
        collection = self.get_collection(collection_name)
        if not collection:
            return {"count": 0}
        
        return {"count": collection.count()}
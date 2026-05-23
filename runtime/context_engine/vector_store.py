
"""ChromaDB vector store wrapper for NeoGodot."""

import uuid
from typing import List, Dict, Any, Optional
from pathlib import Path

from .types import CodeChunk, RetrievedItem


class VectorStore:
    """Simple ChromaDB wrapper for storing and retrieving vectors."""

    def __init__(self, persist_directory: Optional[str] = None):
        """Initialize VectorStore.
        
        Args:
            persist_directory: Directory to persist ChromaDB data. If None,
                              uses in-memory storage.
        """
        self.persist_directory = persist_directory
        self._client = None
        self._collections: Dict[str, Any] = {}
        self._use_chromadb = False
        
        try:
            import chromadb
            from chromadb.utils import embedding_functions
            self._use_chromadb = True
            self._chromadb = chromadb
            self._embedding_functions = embedding_functions
        except ImportError:
            # Fallback to simple implementation without ChromaDB
            self._use_chromadb = False
            self._fallback_collections: Dict[str, List[Dict[str, Any]]] = {}

    def _get_client(self):
        """Get or create ChromaDB client."""
        if not self._use_chromadb:
            return None
            
        if self._client is None:
            if self.persist_directory:
                Path(self.persist_directory).mkdir(parents=True, exist_ok=True)
                self._client = self._chromadb.PersistentClient(
                    path=self.persist_directory
                )
            else:
                self._client = self._chromadb.Client()
        return self._client

    def _get_collection(self, name: str):
        """Get or create a collection by name."""
        if not self._use_chromadb:
            if name not in self._fallback_collections:
                self._fallback_collections[name] = []
            return self._fallback_collections[name]
            
        client = self._get_client()
        if name not in self._collections:
            try:
                self._collections[name] = client.get_collection(name=name)
            except Exception:
                self._collections[name] = client.create_collection(name=name)
        return self._collections[name]

    def add_documents(
        self,
        chunks: List[CodeChunk],
        collection_name: str = "code_chunks",
    ):
        """Add code chunks to the vector store.
        
        Args:
            chunks: List of CodeChunk objects to add
            collection_name: Name of the collection to add to
        """
        if not chunks:
            return
            
        if self._use_chromadb:
            collection = self._get_collection(collection_name)
            
            documents = []
            metadatas = []
            ids = []
            
            for chunk in chunks:
                documents.append(chunk.content)
                metadatas.append({
                    "file_path": chunk.file_path,
                    "chunk_type": chunk.chunk_type,
                    "symbol_name": chunk.symbol_name or "",
                    "start_line": chunk.start_line,
                    "end_line": chunk.end_line,
                })
                ids.append(chunk.chunk_id)
            
            collection.add(
                documents=documents,
                metadatas=metadatas,
                ids=ids,
            )
        else:
            # Fallback implementation
            collection = self._get_collection(collection_name)
            for chunk in chunks:
                collection.append({
                    "id": chunk.chunk_id,
                    "content": chunk.content,
                    "metadata": {
                        "file_path": chunk.file_path,
                        "chunk_type": chunk.chunk_type,
                        "symbol_name": chunk.symbol_name or "",
                        "start_line": chunk.start_line,
                        "end_line": chunk.end_line,
                    },
                })

    def search(
        self,
        query: str,
        collection_name: str = "code_chunks",
        n_results: int = 10,
    ) -&gt; List[RetrievedItem]:
        """Search for relevant chunks using vector similarity.
        
        Args:
            query: Search query string
            collection_name: Name of collection to search in
            n_results: Maximum number of results to return
            
        Returns:
            List of RetrievedItem objects sorted by relevance
        """
        if self._use_chromadb:
            collection = self._get_collection(collection_name)
            
            results = collection.query(
                query_texts=[query],
                n_results=n_results,
            )
            
            items = []
            for i in range(len(results["ids"][0])):
                item = RetrievedItem(
                    content=results["documents"][0][i],
                    source_type="code",
                    source_path=results["metadatas"][0][i]["file_path"],
                    relevance_score=1.0 - results["distances"][0][i] if "distances" in results else 1.0,
                    metadata=results["metadatas"][0][i],
                )
                items.append(item)
            return items
        else:
            # Simple fallback search using keyword matching
            collection = self._get_collection(collection_name)
            query_lower = query.lower()
            
            scored_items = []
            for doc in collection:
                content_lower = doc["content"].lower()
                # Simple scoring: count word matches
                score = sum(
                    1 for word in query_lower.split()
                    if word in content_lower
                )
                if score &gt; 0:
                    scored_items.append((score, doc))
            
            # Sort by score descending
            scored_items.sort(key=lambda x: x[0], reverse=True)
            
            items = []
            for score, doc in scored_items[:n_results]:
                item = RetrievedItem(
                    content=doc["content"],
                    source_type="code",
                    source_path=doc["metadata"]["file_path"],
                    relevance_score=score / max(len(query.split()), 1),
                    metadata=doc["metadata"],
                )
                items.append(item)
            return items

    def delete_by_file_path(
        self,
        file_path: str,
        collection_name: str = "code_chunks",
    ):
        """Delete all chunks associated with a specific file.
        
        Args:
            file_path: Path of the file to delete chunks for
            collection_name: Name of collection to delete from
        """
        if self._use_chromadb:
            collection = self._get_collection(collection_name)
            
            # Get all IDs for the file
            all_results = collection.get()
            ids_to_delete = []
            for i, metadata in enumerate(all_results["metadatas"]):
                if metadata and metadata.get("file_path") == file_path:
                    ids_to_delete.append(all_results["ids"][i])
            
            if ids_to_delete:
                collection.delete(ids=ids_to_delete)
        else:
            # Fallback implementation
            collection = self._get_collection(collection_name)
            self._fallback_collections[collection_name] = [
                doc for doc in collection
                if doc["metadata"]["file_path"] != file_path
            ]

    def clear_collection(self, collection_name: str = "code_chunks"):
        """Clear all documents from a collection.
        
        Args:
            collection_name: Name of collection to clear
        """
        if self._use_chromadb:
            client = self._get_client()
            try:
                client.delete_collection(name=collection_name)
                if collection_name in self._collections:
                    del self._collections[collection_name]
            except Exception:
                pass
        else:
            if collection_name in self._fallback_collections:
                del self._fallback_collections[collection_name]

    def list_collections(self) -&gt; List[str]:
        """List all available collections.
        
        Returns:
            List of collection names
        """
        if self._use_chromadb:
            client = self._get_client()
            return [col.name for col in client.list_collections()]
        else:
            return list(self._fallback_collections.keys())

    def count_documents(self, collection_name: str = "code_chunks") -&gt; int:
        """Count documents in a collection.
        
        Args:
            collection_name: Name of collection to count
            
        Returns:
            Number of documents in the collection
        """
        if self._use_chromadb:
            collection = self._get_collection(collection_name)
            return collection.count()
        else:
            collection = self._get_collection(collection_name)
            return len(collection)


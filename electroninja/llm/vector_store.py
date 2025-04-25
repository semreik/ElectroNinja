# electroninja/llm/vector_store.py

import os
import numpy as np
import logging
import pickle
import openai
from typing import List, Dict, Any, Optional
from electroninja.config.settings import Config

logger = logging.getLogger('electroninja')

class VectorStore:
    """Vector database for storing and retrieving circuit examples using semantic search."""
    
    def __init__(self, config: Optional[Config] = None):
        self.config = config or Config()
        self.embedding_model = "text-embedding-3-small"
        self.vector_size = 1536
        self.metadata_list = []
        self.index = None

        # Set OpenAI API key
        openai.api_key = self.config.OPENAI_API_KEY

        # Import FAISS and initialize index.
        try:
            import faiss
            self.faiss = faiss
            self.index = faiss.IndexFlatL2(self.vector_size)
            logger.info("FAISS index initialized")
        except ImportError:
            logger.error("Failed to import FAISS. Vector search will not be available.")
            self.faiss = None

        # Immediately load existing index if available.
        self.load()

    def load(self) -> bool:
        """
        Load the index and metadata from disk.
        If the files exist, they will be loaded; otherwise, the index remains empty.
        
        Returns:
            bool: True if successfully loaded, False otherwise.
        """
        try:
            if self.faiss is None:
                logger.error("FAISS is not available. Cannot load index.")
                return False

            index_path = self.config.VECTOR_DB_INDEX
            metadata_path = self.config.VECTOR_DB_METADATA

            if os.path.exists(index_path) and os.path.exists(metadata_path):
                self.index = self.faiss.read_index(index_path)
                with open(metadata_path, "rb") as f:
                    self.metadata_list = pickle.load(f)
                logger.info(f"Loaded index with {len(self.metadata_list)} documents")
                return True
            else:
                logger.info("No saved index found. Skipping ingestion from metadata.json.")
                return False
        except Exception as e:
            logger.error(f"Failed to load index: {str(e)}")
            return False

    def save(self) -> bool:
        """
        Save the index and metadata to disk.
        
        Returns:
            bool: True if successfully saved, False otherwise.
        """
        try:
            if self.faiss is None or self.index is None:
                logger.error("FAISS is not available or index is not initialized.")
                return False

            os.makedirs(os.path.dirname(self.config.VECTOR_DB_INDEX), exist_ok=True)
            self.faiss.write_index(self.index, self.config.VECTOR_DB_INDEX)
            with open(self.config.VECTOR_DB_METADATA, "wb") as f:
                pickle.dump(self.metadata_list, f)
            logger.info(f"Saved index with {len(self.metadata_list)} documents")
            return True
        except Exception as e:
            logger.error(f"Failed to save index: {str(e)}")
            return False

    def add_document(self, asc_code: str, metadata: Optional[Dict[str, Any]] = None) -> bool:
        """
        Add a document to the vector store.
        
        Args:
            asc_code (str): ASC code or combined text to embed.
            metadata (dict, optional): Additional metadata.
            
        Returns:
            bool: True if successfully added, False otherwise.
        """
        try:
            if self.faiss is None or self.index is None:
                logger.error("FAISS is not available or index is not initialized.")
                return False

            vector = self.embed_text(asc_code)
            if vector is None:
                logger.error("Failed to compute embedding for the document.")
                return False

            vector = np.expand_dims(vector, axis=0)
            self.index.add(vector)
            doc = {"asc_code": asc_code}
            if metadata:
                doc.update(metadata)
            self.metadata_list.append(doc)
            logger.info(f"Document added. Total documents: {len(self.metadata_list)}")
            return True
        except Exception as e:
            logger.error(f"Failed to add document: {str(e)}")
            return False

    def search(self, query_text: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """
        Search for similar documents.
        
        Args:
            query_text (str): Query text to search for.
            top_k (int): Number of results to return.
            
        Returns:
            list: List of matching documents with metadata and scores.
        """
        try:
            if self.faiss is None or self.index is None:
                logger.error("FAISS is not available or index is not initialized.")
                return []

            if len(self.metadata_list) == 0:
                logger.warning("No documents in the vector store. Returning empty results.")
                return []

            effective_top_k = min(top_k, len(self.metadata_list))
            query_vector = self.embed_text(query_text)
            if query_vector is None:
                logger.error("Failed to compute embedding for the query.")
                return []
            query_vector = np.expand_dims(query_vector, axis=0)
            distances, indices = self.index.search(query_vector, effective_top_k)
            results = []
            for i, idx in enumerate(indices[0]):
                if idx == -1 or idx >= len(self.metadata_list):
                    continue
                metadata = {k: v for k, v in self.metadata_list[idx].items() if k != "asc_code"}
                full_text = self.metadata_list[idx].get("asc_code", "")
                asc_code = full_text.split("\nASC CODE:\n", 1)[1] if "\nASC CODE:\n" in full_text else full_text
                results.append({
                    "asc_code": asc_code,
                    "metadata": metadata,
                    "score": float(distances[0][i])
                })
            logger.info(f"Found {len(results)} similar documents for query: '{query_text[:50]}...'")
            return results
        except Exception as e:
            logger.error(f"Search error: {str(e)}")
            return []

    def embed_text(self, text: str) -> Optional[np.ndarray]:
        """
        Generate an embedding for text.
        
        Args:
            text (str): Text to embed.
            
        Returns:
            np.ndarray: Embedding vector, or None if embedding fails.
        """
        try:
            text = text.replace("\n", " ")
            response = openai.Embedding.create(
                input=[text],
                model=self.embedding_model
            )
            embedding = response["data"][0]["embedding"]
            return np.array(embedding, dtype=np.float32)
        except Exception as e:
            logger.error(f"Embedding error: {str(e)}")
            return None

    def get_document_count(self) -> int:
        """Return the number of documents in the index."""
        return len(self.metadata_list)

    def clear(self) -> bool:
        """Clear the index and metadata."""
        if self.faiss is not None:
            self.index = self.faiss.IndexFlatL2(self.vector_size)
            self.metadata_list = []
            logger.info("Index and metadata cleared")
            return True
        return False

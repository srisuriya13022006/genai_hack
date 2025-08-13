import json
import numpy as np
from pathlib import Path
import logging
import faiss
from sentence_transformers import SentenceTransformer
from typing import List, Dict, Tuple

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Load pre-trained SentenceTransformers model
model = SentenceTransformer('all-MiniLM-L6-v2')  # Matches embedder model

class QueryProcessor:
    """Processes queries by encoding them and searching the FAISS index."""
    
    def __init__(self, index_path: str, metadata_path: str, chunks_path: str, top_k: int = 10):
        """Initialize the query processor with index, metadata, and chunks paths.
        
        Args:
            index_path (str): Path to the FAISS index file.
            metadata_path (str): Path to the metadata JSON file.
            chunks_path (str): Path to the processed chunks JSON file.
            top_k (int): Number of top results to return (default: 10).
        """
        self.index = faiss.read_index(index_path)
        self.metadata = self._load_metadata(metadata_path)
        self.chunks = self._load_chunks(chunks_path)
        self.top_k = top_k
    
    def _load_metadata(self, metadata_path: str) -> Dict[int, Dict]:
        """Load metadata from a JSON file.
        
        Args:
            metadata_path (str): Path to the metadata JSON file.
        
        Returns:
            Dict[int, Dict]: Dictionary mapping index IDs to metadata.
        """
        try:
            with Path(metadata_path).open("r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading metadata from {metadata_path}: {str(e)}")
            return {}
    
    def _load_chunks(self, chunks_path: str) -> List[str]:
        """Load chunks from a JSON file.
        
        Args:
            chunks_path (str): Path to the processed chunks JSON file.
        
        Returns:
            List[str]: List of chunk texts.
        """
        try:
            with Path(chunks_path).open("r", encoding="utf-8") as f:
                data = json.load(f)
                return data["chunks"]
        except Exception as e:
            logger.error(f"Error loading chunks from {chunks_path}: {str(e)}")
            return []
    
    def encode_query(self, query: str) -> np.ndarray:
        """Encode a query into an embedding.
        
        Args:
            query (str): User query text.
        
        Returns:
            np.ndarray: Query embedding.
        """
        try:
            embedding = model.encode([query], convert_to_numpy=True)
            logger.info("Encoded query successfully")
            return embedding[0]
        except Exception as e:
            logger.error(f"Error encoding query: {str(e)}")
            return np.array([])
    
    def search_index(self, query_embedding: np.ndarray) -> List[Tuple[int, float]]:
        """Search the FAISS index for the top-k nearest neighbors.
        
        Args:
            query_embedding (np.ndarray): Embedding of the query.
        
        Returns:
            List[Tuple[int, float]]: List of (index_id, distance) pairs.
        """
        if query_embedding.size == 0 or self.index.ntotal == 0:
            logger.warning("Empty query embedding or index")
            return []
        
        distances, indices = self.index.search(query_embedding.reshape(1, -1), self.top_k)
        print("Distances:", distances)  # Debug: Print distances to inspect
        return list(zip(indices[0], distances[0]))
    
    def get_results(self, query: str) -> List[Dict]:
        """Process a query and return top-k results with metadata and chunk text.
        
        Args:
            query (str): User query text.
        
        Returns:
            List[Dict]: List of results with doc_name, chunk_id, distance, and chunk_text.
        """
        query_embedding = self.encode_query(query)
        if query_embedding.size == 0:
            return []
        
        results = self.search_index(query_embedding)
        output = []
        for idx, distance in results:
            if str(idx) in self.metadata:
                meta = self.metadata[str(idx)]
                chunk_text = self.chunks[idx] if idx < len(self.chunks) else "Chunk not found"
                output.append({
                    "doc_name": meta["doc_name"],
                    "chunk_id": meta["chunk_id"],
                    "distance": float(distance),
                    "chunk_text": chunk_text
                })
        logger.info(f"Retrieved {len(output)} results for query: {query}")
        return output

def main():
    """Example usage of QueryProcessor."""
    index_path = "indexes/faiss_index.bin"
    metadata_path = "indexes/faiss_metadata.json"
    chunks_path = "data/processed/chunks/Unit 1_text_processed.json"  # Path to your JSON
    processor = QueryProcessor(index_path, metadata_path, chunks_path, top_k=10)
    query = "tell what are the topics are there in this file"
    results = processor.get_results(query)
    for result in results:
        logger.info(f"Result: {result}")

if __name__ == "__main__":
    main()

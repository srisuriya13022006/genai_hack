# FAISS indexing logic
import json
import numpy as np
from pathlib import Path
import logging
import faiss
from typing import List, Dict, Optional

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

class FAISSIndexer:
    """Creates and manages a FAISS index for embeddings with associated metadata."""
    
    def __init__(self, input_dir: str, index_dir: str):
        """Initialize the indexer with input and index directories.
        
        Args:
            input_dir (str): Directory containing embedding NumPy files.
            index_dir (str): Directory to store FAISS index and metadata.
        """
        self.input_dir = Path(input_dir)
        self.index_dir = Path(index_dir)
        self.index_dir.mkdir(parents=True, exist_ok=True)
        self.index = None
        self.metadata = {}
    
    def build_index(self, embeddings: np.ndarray, doc_name: str, chunk_ids: List[int]):
        """Build or update the FAISS index with new embeddings.
        
        Args:
            embeddings (np.ndarray): Array of embeddings.
            doc_name (str): Name of the document.
            chunk_ids (List[int]): List of chunk indices.
        """
        if embeddings.size == 0:
            logger.warning("Empty embeddings provided")
            return
        
        dimension = embeddings.shape[1]
        if self.index is None:
            self.index = faiss.IndexFlatL2(dimension)  # L2 distance index
        
        self.index.add(embeddings)
        for idx, chunk_id in enumerate(chunk_ids):
            self.metadata[len(self.metadata)] = {"doc_name": doc_name, "chunk_id": chunk_id}
        logger.info(f"Added {embeddings.shape[0]} embeddings to index")
    
    def process_document(self, npy_path: Path) -> Optional[Dict[str, int]]:
        """Process a single embedding file and update the index.
        
        Args:
            npy_path (Path): Path to the embedding NumPy file.
        
        Returns:
            Optional[Dict[str, int]]: Dictionary with doc name and total embeddings, or None if processing fails.
        """
        try:
            embeddings = np.load(npy_path)
            doc_name = npy_path.stem.replace("_embeddings", "")
            chunk_ids = list(range(embeddings.shape[0]))
            
            self.build_index(embeddings, doc_name, chunk_ids)
            
            # Save index and metadata
            index_path = self.index_dir / "faiss_index.bin"
            faiss.write_index(self.index, index_path.as_posix())
            metadata_path = self.index_dir / "faiss_metadata.json"
            with metadata_path.open("w", encoding="utf-8") as f:
                json.dump(self.metadata, f, ensure_ascii=False, indent=2)
            logger.info(f"Saved index to {index_path} and metadata to {metadata_path}")
            return {"doc_name": doc_name, "total_embeddings": embeddings.shape[0]}
        
        except Exception as e:
            logger.error(f"Error processing {npy_path}: {str(e)}")
            return None
    
    def process_all_documents(self) -> List[Dict[str, int]]:
        """Process all embedding files in the input directory.
        
        Returns:
            List[Dict[str, int]]: List of document data with total embeddings.
        """
        indexed_docs = []
        npy_files = list(self.input_dir.glob("*.npy"))
        
        if not npy_files:
            logger.warning(f"No NumPy files found in {self.input_dir}")
            return indexed_docs
        
        for npy_path in npy_files:
            indexed_data = self.process_document(npy_path)
            if indexed_data:
                indexed_docs.append(indexed_data)
        
        logger.info(f"Processed {len(indexed_docs)} documents")
        return indexed_docs

def main():
    """Example usage of FAISSIndexer."""
    input_dir = "data/processed/embeddings"
    index_dir = "indexes"
    indexer = FAISSIndexer(input_dir, index_dir)
    indexed_docs = indexer.process_all_documents()

if __name__ == "__main__":
    main()

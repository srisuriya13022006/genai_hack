import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import json
from pathlib import Path
import logging
from typing import List, Dict, Tuple
from preprocessing.text_cleaner import TextCleaner
from embedding.embedder import Embedder
from indexing.faiss_indexer import FAISSIndexer
from query.query_processor import QueryProcessor

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

class StudyMatePipeline:
    """Orchestrates the full data processing and querying pipeline."""
    
    def __init__(self, raw_dir: str, chunks_dir: str, embeddings_dir: str, index_dir: str):
        """Initialize the pipeline with directory paths.
        
        Args:
            raw_dir (str): Directory for raw text JSON files.
            chunks_dir (str): Directory for processed chunk JSON files.
            embeddings_dir (str): Directory for embedding NumPy files.
            index_dir (str): Directory for FAISS index and metadata.
        """
        self.raw_dir = Path(raw_dir)
        self.chunks_dir = Path(chunks_dir)
        self.embeddings_dir = Path(embeddings_dir)
        self.index_dir = Path(index_dir)
        self.chunks_dir.mkdir(parents=True, exist_ok=True)
        self.embeddings_dir.mkdir(parents=True, exist_ok=True)
        self.index_dir.mkdir(parents=True, exist_ok=True)
    
    def process_data(self):
        """Run the preprocessing, embedding, and indexing steps."""
        # Step 1: Clean and chunk text
        cleaner = TextCleaner(str(self.raw_dir), str(self.chunks_dir), chunk_size=512, overlap=50)
        cleaned_texts = cleaner.process_all_documents()
        logger.info(f"Completed text cleaning for {len(cleaned_texts)} documents")
        
        # Step 2: Generate embeddings
        embedder = Embedder(str(self.chunks_dir), str(self.embeddings_dir))
        embedded_docs = embedder.process_all_documents()
        logger.info(f"Completed embedding for {len(embedded_docs)} documents")
        
        # Step 3: Build FAISS index
        indexer = FAISSIndexer(str(self.embeddings_dir), str(self.index_dir))
        indexed_docs = indexer.process_all_documents()
        logger.info(f"Completed indexing for {len(indexed_docs)} documents")
        return indexed_docs
    
    def query(self, query_text: str, top_k: int = 10) -> List[Dict]:
        """Process a query and return top-k results.
        
        Args:
            query_text (str): User query text.
            top_k (int): Number of top results to return (default: 10).
        
        Returns:
            List[Dict]: List of results with doc_name, chunk_id, distance, and chunk_text.
        """
        chunks_path = next(self.chunks_dir.glob("*.json"), None)
        if not chunks_path:
            logger.error("No processed chunks found")
            return []
        
        processor = QueryProcessor(
            str(self.index_dir / "faiss_index.bin"),
            str(self.index_dir / "faiss_metadata.json"),
            str(chunks_path),
            top_k=top_k
        )
        results = processor.get_results(query_text)
        return results

def main():
    """Example usage of the StudyMatePipeline."""
    pipeline = StudyMatePipeline(
        raw_dir="data/processed/raw_text",
        chunks_dir="data/processed/chunks",
        embeddings_dir="data/processed/embeddings",
        index_dir="indexes"
    )
    
    # Process the data
    indexed_docs = pipeline.process_data()
    
    # Query the data
    query_text = "What is Data Science?"
    results = pipeline.query(query_text, top_k=10)
    for result in results:
        logger.info(f"Result: {result}")

if __name__ == "__main__":
    main()

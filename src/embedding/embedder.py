import json
from pathlib import Path
import logging
import numpy as np
from sentence_transformers import SentenceTransformer
from typing import List, Dict, Optional

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Load pre-trained SentenceTransformers model
model = SentenceTransformer('all-MiniLM-L6-v2')  # 384-dimensional embeddings

class Embedder:
    """Generates embeddings for cleaned and chunked text using SentenceTransformers."""
    
    def __init__(self, input_dir: str, output_dir: str):
        """Initialize the embedder with input and output directories.
        
        Args:
            input_dir (str): Directory containing processed JSON files.
            output_dir (str): Directory to store embedding NumPy arrays.
        """
        self.input_dir = Path(input_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def generate_embeddings(self, chunks: List[str]) -> Optional[np.ndarray]:
        """Generate embeddings for a list of text chunks.
        
        Args:
            chunks (List[str]): List of text chunks.
        
        Returns:
            Optional[np.ndarray]: Array of embeddings, or None if generation fails.
        """
        try:
            if not chunks:
                logger.warning("No chunks provided for embedding")
                return None
            
            embeddings = model.encode(chunks, convert_to_numpy=True)
            logger.info(f"Generated embeddings for {len(chunks)} chunks")
            return embeddings
        except Exception as e:
            logger.error(f"Error generating embeddings: {str(e)}")
            return None
    
    def process_document(self, json_path: Path) -> Optional[Dict[str, np.ndarray]]:
        """Generate embeddings for chunks in a single JSON file and save them.
        
        Args:
            json_path (Path): Path to the processed JSON file.
        
        Returns:
            Optional[Dict[str, np.ndarray]]: Dictionary with doc name and embeddings, or None if processing fails.
        """
        try:
            with json_path.open("r", encoding="utf-8") as f:
                processed_data = json.load(f)
            
            embeddings = self.generate_embeddings(processed_data["chunks"])
            if embeddings is not None:
                output_path = self.output_dir / f"{json_path.stem}_embeddings.npy"
                np.save(output_path, embeddings)
                logger.info(f"Saved embeddings to {output_path}")
                return {"doc_name": processed_data["doc_name"], "embeddings": embeddings}
            return None
        
        except Exception as e:
            logger.error(f"Error processing {json_path}: {str(e)}")
            return None
    
    def process_all_documents(self) -> List[Dict[str, np.ndarray]]:
        """Process all JSON files in the input directory.
        
        Returns:
            List[Dict[str, np.ndarray]]: List of document data with embeddings.
        """
        embedded_docs = []
        json_files = list(self.input_dir.glob("*.json"))
        
        if not json_files:
            logger.warning(f"No JSON files found in {self.input_dir}")
            return embedded_docs
        
        for json_path in json_files:
            embedded_data = self.process_document(json_path)
            if embedded_data:
                embedded_docs.append(embedded_data)
        
        logger.info(f"Processed {len(embedded_docs)} documents")
        return embedded_docs

def main():
    """Example usage of Embedder."""
    input_dir = "data/processed/chunks"
    output_dir = "data/processed/embeddings"
    embedder = Embedder(input_dir, output_dir)
    embedded_docs = embedder.process_all_documents()

if __name__ == "__main__":
    main()
# Script to run pipeline
import sys
import os
import yaml
import argparse
import json
from pathlib import Path
import logging

# Add the parent directory of src to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.pipeline import StudyMatePipeline  # Import the pipeline class

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

def load_config(config_path: str) -> dict:
    """Load configuration from a YAML file."""
    try:
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f) or {}
            # Provide default values if keys are missing
            return {
                "raw_dir": config.get("raw_dir", "data/processed/raw_text"),
                "chunks_dir": config.get("chunks_dir", "data/processed/chunks"),
                "embeddings_dir": config.get("embeddings_dir", "data/processed/embeddings"),
                "index_dir": config.get("index_dir", "indexes"),
                "chunk_size": config.get("chunk_size", 512),
                "overlap": config.get("overlap", 50),
                "top_k": config.get("top_k", 10)
            }
    except FileNotFoundError:
        logger.warning(f"Config file {config_path} not found, using default values")
        return {
            "raw_dir": "data/processed/raw_text",
            "chunks_dir": "data/processed/chunks",
            "embeddings_dir": "data/processed/embeddings",
            "index_dir": "indexes",
            "chunk_size": 512,
            "overlap": 50,
            "top_k": 10
        }

def get_processed_files(metadata_path: str) -> set:
    """Get set of processed file names from metadata."""
    if not Path(metadata_path).exists():
        return set()
    with open(metadata_path, 'r') as f:
        metadata = json.load(f)
        return {meta["doc_name"] for meta in metadata.values()}

def main():
    """Main function with CLI and pipeline execution."""
    parser = argparse.ArgumentParser(description="StudyMate Pipeline for Data Science Queries")
    parser.add_argument('--query', type=str, help="Query to process", default="What is Data Science?")
    parser.add_argument('--config', type=str, default="config.yaml", help="Path to configuration file")
    parser.add_argument('--reprocess', action='store_true', help="Force reprocess all data")
    args = parser.parse_args()

    # Load configuration
    config = load_config(args.config)
    raw_dir = config["raw_dir"]
    chunks_dir = config["chunks_dir"]
    embeddings_dir = config["embeddings_dir"]
    index_dir = config["index_dir"]
    chunk_size = config["chunk_size"]
    overlap = config["overlap"]
    top_k = config["top_k"]

    # Initialize pipeline
    pipeline = StudyMatePipeline(raw_dir, chunks_dir, embeddings_dir, index_dir)

    # Check for new or updated files
    metadata_path = Path(index_dir) / "faiss_metadata.json"
    processed_files = get_processed_files(metadata_path)
    raw_files = {f.stem for f in Path(raw_dir).glob("*.json")}
    new_or_updated_files = raw_files - processed_files

    # Process data if new files are detected or reprocess is forced
    if new_or_updated_files or args.reprocess or not (Path(index_dir) / "faiss_index.bin").exists():
        pipeline.process_data(chunk_size, overlap)
    else:
        logger.info("No new files detected, using existing index and data")

    # Query the data
    results = pipeline.query(args.query, top_k)
    for result in results:
        logger.info(f"Result: {result}")

if __name__ == "__main__":
    main()
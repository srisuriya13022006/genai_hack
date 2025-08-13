# import sys
# import os
# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# import json
# from pathlib import Path
# import logging
# from typing import List, Dict, Tuple
# from preprocessing.text_cleaner import TextCleaner
# from embedding.embedder import Embedder
# from indexing.faiss_indexer import FAISSIndexer
# from query.query_processor import QueryProcessor

# # Configure logging
# logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
# logger = logging.getLogger(__name__)

# class StudyMatePipeline:
#     """Orchestrates the full data processing and querying pipeline."""
    
#     def __init__(self, raw_dir: str, chunks_dir: str, embeddings_dir: str, index_dir: str):
#         """Initialize the pipeline with directory paths.
        
#         Args:
#             raw_dir (str): Directory for raw text JSON files.
#             chunks_dir (str): Directory for processed chunk JSON files.
#             embeddings_dir (str): Directory for embedding NumPy files.
#             index_dir (str): Directory for FAISS index and metadata.
#         """
#         self.raw_dir = Path(raw_dir)
#         self.chunks_dir = Path(chunks_dir)
#         self.embeddings_dir = Path(embeddings_dir)
#         self.index_dir = Path(index_dir)
#         self.chunks_dir.mkdir(parents=True, exist_ok=True)
#         self.embeddings_dir.mkdir(parents=True, exist_ok=True)
#         self.index_dir.mkdir(parents=True, exist_ok=True)
    
#     def process_data(self):
#         """Run the preprocessing, embedding, and indexing steps."""
#         # Step 1: Clean and chunk text
#         cleaner = TextCleaner(str(self.raw_dir), str(self.chunks_dir), chunk_size=512, overlap=50)
#         cleaned_texts = cleaner.process_all_documents()
#         logger.info(f"Completed text cleaning for {len(cleaned_texts)} documents")
        
#         # Step 2: Generate embeddings
#         embedder = Embedder(str(self.chunks_dir), str(self.embeddings_dir))
#         embedded_docs = embedder.process_all_documents()
#         logger.info(f"Completed embedding for {len(embedded_docs)} documents")
        
#         # Step 3: Build FAISS index
#         indexer = FAISSIndexer(str(self.embeddings_dir), str(self.index_dir))
#         indexed_docs = indexer.process_all_documents()
#         logger.info(f"Completed indexing for {len(indexed_docs)} documents")
#         return indexed_docs
    
#     def query(self, query_text: str, top_k: int = 10) -> List[Dict]:
#         """Process a query and return top-k results.
        
#         Args:
#             query_text (str): User query text.
#             top_k (int): Number of top results to return (default: 10).
        
#         Returns:
#             List[Dict]: List of results with doc_name, chunk_id, distance, and chunk_text.
#         """
#         chunks_path = next(self.chunks_dir.glob("*.json"), None)
#         if not chunks_path:
#             logger.error("No processed chunks found")
#             return []
        
#         processor = QueryProcessor(
#             str(self.index_dir / "faiss_index.bin"),
#             str(self.index_dir / "faiss_metadata.json"),
#             str(chunks_path),
#             top_k=top_k
#         )
#         results = processor.get_results(query_text)
#         return results

# def main():
#     """Example usage of the StudyMatePipeline."""
#     pipeline = StudyMatePipeline(
#         raw_dir="data/processed/raw_text",
#         chunks_dir="data/processed/chunks",
#         embeddings_dir="data/processed/embeddings",
#         index_dir="indexes"
#     )
    
#     # Process the data
#     indexed_docs = pipeline.process_data()
    
#     # Query the data
#     query_text = "What is Data Science?"
#     results = pipeline.query(query_text, top_k=10)
#     for result in results:
#         logger.info(f"Result: {result}")

# if __name__ == "__main__":
#     main()
import sys
import os
import yaml
import argparse
import json
from pathlib import Path
import logging
from typing import List, Dict
import google.generativeai as genai
from dotenv import load_dotenv
import time
from flask import Flask, request, jsonify

# Import PDFExtractor
from src.extraction.pdf_extractor import PDFExtractor

# Other dependencies
from src.preprocessing.text_cleaner import TextCleaner
from src.embedding.embedder import Embedder
from src.indexing.faiss_indexer import FAISSIndexer
from src.query.query_processor import QueryProcessor

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Adjust sys.path to include src
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Load environment variables from .env file
load_dotenv()

# Configure Gemini API key from environment variable
genai.configure(api_key=os.getenv('GEMINI_API_KEY'))

app = Flask(__name__)

def load_config(config_path: str) -> dict:
    """Load configuration from a YAML file."""
    try:
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f) or {}
            return {
                "raw_dir": config.get("raw_dir", "data/processed/raw_text"),
                "chunks_dir": config.get("chunks_dir", "data/processed/chunks"),
                "embeddings_dir": config.get("embeddings_dir", "data/processed/embeddings"),
                "index_dir": config.get("index_dir", "indexes"),
                "input_dir": config.get("input_dir", "data/input/textbooks"),
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
            "input_dir": "data/input/textbooks",
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

def get_processed_pdfs(raw_dir: str) -> set:
    """Get set of processed PDF base names from raw JSON files."""
    return {f.stem.replace("_text", "") for f in Path(raw_dir).glob("*.json")}

def load_chunk_text(chunks_dir: str, doc_name: str, chunk_id: int) -> str:
    """Load text for a specific chunk from the processed chunk file."""
    chunk_file = Path(chunks_dir) / f"{doc_name}.json"
    if not chunk_file.exists():
        logger.error(f"Chunk file not found for {doc_name}")
        return "Chunk not found"
    try:
        with open(chunk_file, 'r') as f:
            data = json.load(f)
            chunks = data.get("chunks", [])
            if 0 <= chunk_id < len(chunks):
                return chunks[chunk_id]
            logger.error(f"Chunk ID {chunk_id} out of range for {doc_name}")
            return "Chunk not found"
    except Exception as e:
        logger.error(f"Error reading chunk file {doc_name}.json: {str(e)}")
        return "Chunk not found"

def process_new_pdfs(pipeline: 'StudyMatePipeline', input_dir: str) -> None:
    """Process any new or unprocessed PDFs in the input directory."""
    extractor = PDFExtractor(input_dir, pipeline.raw_dir)
    pdf_files = list(Path(input_dir).glob("*.pdf"))
    if not pdf_files:
        logger.info("No new PDFs to process")
        return

    logger.info(f"Processing {len(pdf_files)} PDFs")
    extracted_texts = extractor.process_pdfs(pdf_files)  # Pass list of PDFs
    if extracted_texts:
        pipeline.process_data()

def main():
    """Main function with CLI and pipeline execution."""
    parser = argparse.ArgumentParser(description="StudyMate Pipeline for Data Science Queries")
    parser.add_argument('--query', type=str, help="Query to process", default="What is Data Science?")
    parser.add_argument('--config', type=str, default="config.yaml", help="Path to configuration file")
    parser.add_argument('--reprocess', action='store_true', help="Force reprocess all data")
    parser.add_argument('--model', type=str, default="gemini-2.0-flash", help="Gemini model to use (e.g., gemini-2.0-flash or gemini-1.5-pro)")
    parser.add_argument('--no-api', action='store_true', help="Run CLI mode without starting the API server")
    args = parser.parse_args()

    # Load configuration
    config = load_config(args.config)
    raw_dir = config["raw_dir"]
    chunks_dir = config["chunks_dir"]
    embeddings_dir = config["embeddings_dir"]
    index_dir = config["index_dir"]
    input_dir = config["input_dir"]
    chunk_size = config["chunk_size"]
    overlap = config["overlap"]
    top_k = config["top_k"]

    # Ensure directories exist
    for directory in [raw_dir, chunks_dir, embeddings_dir, index_dir, input_dir]:
        Path(directory).mkdir(parents=True, exist_ok=True)

    # Initialize pipeline
    pipeline = StudyMatePipeline(raw_dir, chunks_dir, embeddings_dir, index_dir)

    # Process all data on startup if reprocess or no index exists
    if args.reprocess or not (Path(index_dir) / "faiss_index.bin").exists():
        pipeline.process_data(chunk_size, overlap)
    else:
        logger.info("Using existing index and data")

    # Query the data and generate answer in CLI mode
    if args.no_api:
        results = pipeline.query(args.query, top_k)
        for result in results:
            result['chunk_text'] = load_chunk_text(chunks_dir, result['doc_name'], result['chunk_id'])
            logger.info(f"Result: {result}")
        answer = pipeline.generate_answer(args.query, results, model=args.model)
        logger.info(f"Generated Answer: {answer}")
    else:
        # Start Flask API server
        app.pipeline = pipeline
        app.config['chunks_dir'] = chunks_dir
        app.config['model'] = args.model
        app.config['input_dir'] = input_dir
        app.run(debug=True, host='0.0.0.0', port=5000)

@app.route('/upload', methods=['POST'])
def handle_upload():
    """Endpoint to upload a PDF and save it."""
    if 'file' not in request.files:
        return jsonify({"error": "No file part in the request"}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400
    if not file.filename.endswith('.pdf'):
        return jsonify({"error": "Only PDF files are allowed"}), 400

    pdf_path = Path(app.config['input_dir']) / file.filename
    file.save(pdf_path)
    logger.info(f"Uploaded PDF saved to {pdf_path}")
    return jsonify({"message": f"Successfully uploaded {file.filename}"}), 200

@app.route('/query', methods=['POST'])
def handle_query():
    """Endpoint to process a query and return results and answer."""
    data = request.get_json()
    if not data or 'query' not in data:
        return jsonify({"error": "No query provided"}), 400

    query_text = data['query']
    top_k = data.get('top_k', 10)
    model = app.config.get('model', 'gemini-2.0-flash')

    # Use the pipeline instance stored in the app
    pipeline = app.pipeline
    # Process any new PDFs before querying
    process_new_pdfs(pipeline, app.config['input_dir'])
    results = pipeline.query(query_text, top_k)
    for result in results:
        result['chunk_text'] = load_chunk_text(app.config['chunks_dir'], result['doc_name'], result['chunk_id'])

    answer = pipeline.generate_answer(query_text, results, model=model)

    response = {
        "query": query_text,
        "results": results,
        "answer": answer
    }
    return jsonify(response)

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
    
    def process_data(self, chunk_size: int = 512, overlap: int = 50):
        """Run the preprocessing, embedding, and indexing steps."""
        # Step 1: Clean and chunk text
        cleaner = TextCleaner(str(self.raw_dir), str(self.chunks_dir), chunk_size=chunk_size, overlap=overlap)
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
            List[Dict]: Dictionary mapping index IDs to metadata.
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

    def generate_answer(self, query_text: str, results: List[Dict], model: str = "gemini-2.0-flash") -> str:
        """Generate an answer using Gemini based on the retrieved chunks.
        
        Args:
            query_text (str): User query text.
            results (List[Dict]): Retrieved results with chunk_text.
            model (str): Gemini model to use (default: gemini-2.0-flash).
        
        Returns:
            str: Generated answer from Gemini.
        """
        # Limit to top 3 chunks to reduce token usage
        results = sorted(results, key=lambda x: x['distance'])[:3]
        
        # Format context from retrieved chunks
        context = ""
        for result in results:
            context += f"Chunk ID: {result['chunk_id']}\nDistance: {result['distance']}\nText: {result['chunk_text']}\n\n"

        if not context:
            logger.warning("No context available for Gemini generation")
            return "No relevant information found."

        # Prompt for Gemini
        prompt = f"Based on the following context from retrieved documents, provide a clear and concise answer to the query: '{query_text}'.\n\nContext:\n{context}"

        # Call Gemini with retry logic
        max_retries = 3
        for attempt in range(max_retries):
            try:
                model_instance = genai.GenerativeModel(model)
                response = model_instance.generate_content(prompt)
                return response.text
            except genai.types.GenerativeModelError as e:
                if e.status_code == 429 and attempt < max_retries - 1:
                    logger.warning(f"Quota exceeded, retrying in 17 seconds (Attempt {attempt + 1}/{max_retries})")
                    time.sleep(17)  # Retry delay as suggested
                else:
                    logger.error(f"Error generating answer with Gemini: {str(e)}")
                    return "Failed to generate answer."

        return "Failed to generate answer after retries."

if __name__ == "__main__":
    main()

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
from flask_cors import CORS

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
# Enable CORS for all routes
CORS(app, resources={r"/*": {"origins": "*"}})

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
        with open(chunk_file, 'r', encoding='utf-8') as f:
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
    extracted_texts = extractor.process_pdfs(pdf_files)
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
    # Process the new PDF immediately
    process_new_pdfs(app.pipeline, app.config['input_dir'])
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

@app.route('/uploaded_files', methods=['GET'])
def get_uploaded_files():
    """Endpoint to return the list of uploaded and processed files."""
    input_dir = app.config['input_dir']
    pdf_files = list(Path(input_dir).glob("*.pdf"))
    files = []
    for pdf in pdf_files:
        # Assume topic is derived from the filename (simplified)
        # In a real implementation, you might extract topics using a model
        files.append({
            "name": pdf.name,
            "type": "application/pdf",
            "topics": [pdf.stem],  # Simplified topic extraction
            "url": f"/files/{pdf.name}"  # Placeholder URL
        })
    return jsonify({"files": files})

@app.route('/resources', methods=['GET'])
def get_resources():
    """Endpoint to generate and return recommended resources based on processed raw text using Gemini."""
    pipeline = app.pipeline
    model = app.config.get('model', 'gemini-2.0-flash')
    resources = pipeline.generate_resources(model)
    return jsonify(resources)

@app.route('/quiz', methods=['GET'])
def get_quiz():
    topic = request.args.get('topic')
    difficulty = request.args.get('difficulty', 'medium')
    if not topic:
        return jsonify({"error": "Topic is required"}), 400
    pipeline = app.pipeline
    model = app.config.get('model', 'gemini-2.0-flash')
    questions = pipeline.generate_quiz(topic, difficulty, model)
    return jsonify({"questions": questions})

class StudyMatePipeline:
    """Orchestrates the full data processing and querying pipeline."""
    
    def __init__(self, raw_dir: str, chunks_dir: str, embeddings_dir: str, index_dir: str):
        """Initialize the pipeline with directory paths."""
        self.raw_dir = Path(raw_dir)
        self.chunks_dir = Path(chunks_dir)
        self.embeddings_dir = Path(embeddings_dir)
        self.index_dir = Path(index_dir)
        self.chunks_dir.mkdir(parents=True, exist_ok=True)
        self.embeddings_dir.mkdir(parents=True, exist_ok=True)
        self.index_dir.mkdir(parents=True, exist_ok=True)
    
    def process_data(self, chunk_size: int = 512, overlap: int = 50):
        """Run the preprocessing, embedding, and indexing steps."""
        cleaner = TextCleaner(str(self.raw_dir), str(self.chunks_dir), chunk_size=chunk_size, overlap=overlap)
        cleaned_texts = cleaner.process_all_documents()
        logger.info(f"Completed text cleaning for {len(cleaned_texts)} documents")
        
        embedder = Embedder(str(self.chunks_dir), str(self.embeddings_dir))
        embedded_docs = embedder.process_all_documents()
        logger.info(f"Completed embedding for {len(embedded_docs)} documents")
        
        indexer = FAISSIndexer(str(self.embeddings_dir), str(self.index_dir))
        indexed_docs = indexer.process_all_documents()
        logger.info(f"Completed indexing for {len(indexed_docs)} documents")
        return indexed_docs
    
    def query(self, query_text: str, top_k: int = 10) -> List[Dict]:
        """Process a query and return top-k results."""
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
        """Generate an answer using Gemini based on the retrieved chunks."""
        results = sorted(results, key=lambda x: x['distance'])[:3]
        context = ""
        for result in results:
            context += f"Chunk ID: {result['chunk_id']}\nDistance: {result['distance']}\nText: {result['chunk_text']}\n\n"

        if not context:
            logger.warning("No context available for Gemini generation")
            return "No relevant information found."

        prompt = f"Based on the following context from retrieved documents, provide a clear and concise answer to the query: '{query_text}'.\n\nContext:\n{context}"

        max_retries = 3
        for attempt in range(max_retries):
            try:
                model_instance = genai.GenerativeModel(model)
                response = model_instance.generate_content(prompt)
                return response.text
            except Exception as e:
                logger.error(f"Error generating answer with Gemini: {str(e)}")
                if attempt < max_retries - 1:
                    logger.warning(f"Retrying in 17 seconds (Attempt {attempt + 1}/{max_retries})")
                    time.sleep(17)
                else:
                    return "Failed to generate answer after retries."
        return "Failed to generate answer after retries."

    def generate_resources(self, model: str) -> Dict[str, List[Dict]]:
        """Generate recommended resources using Gemini based on raw text content."""
        resources_list = []
        json_files = list(self.raw_dir.glob("*_text.json"))
        for json_file in json_files:
            doc_name = json_file.stem.replace('_text', '')
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    text = data.get('text', '')
                context = text[:2000]  # Limit for token safety
                prompt = f"Based on the document topic '{doc_name}' and content snippet: {context}\n\n" \
                         f"Generate exactly 6 relevant real-world learning resources to enhance understanding of this topic.\n" \
                         f"Return ONLY a valid JSON array with 6 objects: 2 videos, 2 articles, 1 interactive, 1 book.\n" \
                         f"Do NOT include any explanatory text, just the JSON array.\n" \
                         f"Use actual titles, authors, URLs, and video IDs from sources like YouTube, Harvard Business Review, Khan Academy, Amazon, GeoGebra, PhET, etc.\n" \
                         f"Example structure (fill with real data):\n" \
                         f"[\n" \
                         f"  {{\"type\": \"video\", \"category\": \"video\", \"title\": \"...\", \"description\": \"...\", \"url\": \"https://www.youtube.com/embed/VIDEO_ID\", \"thumbnail\": \"https://img.youtube.com/vi/VIDEO_ID/maxresdefault.jpg\", \"duration\": \"MM:SS\", \"difficulty\": \"Beginner|Intermediate|Advanced\", \"rating\": 4.5, \"views\": \"1M\", \"author\": \"...\", \"tags\": [\"tag1\", \"tag2\"]}},\n" \
                         f"  {{\"type\": \"video\", \"category\": \"video\", \"title\": \"...\", \"description\": \"...\", \"url\": \"https://www.youtube.com/embed/VIDEO_ID\", \"thumbnail\": \"https://img.youtube.com/vi/VIDEO_ID/maxresdefault.jpg\", \"duration\": \"MM:SS\", \"difficulty\": \"Beginner|Intermediate|Advanced\", \"rating\": 4.5, \"views\": \"1M\", \"author\": \"...\", \"tags\": [\"tag1\", \"tag2\"]}},\n" \
                         f"  {{\"type\": \"article\", \"category\": \"article\", \"title\": \"...\", \"description\": \"...\", \"url\": \"https://example.com/article\", \"thumbnail\": \"https://via.placeholder.com/300x200?text=Article\", \"readTime\": \"10 min read\", \"difficulty\": \"Intermediate\", \"rating\": 4.6, \"publishDate\": \"YYYY-MM-DD\", \"author\": \"...\", \"tags\": [\"tag1\", \"tag2\"]}},\n" \
                         f"  {{\"type\": \"article\", \"category\": \"article\", \"title\": \"...\", \"description\": \"...\", \"url\": \"https://example.com/article\", \"thumbnail\": \"https://via.placeholder.com/300x200?text=Article\", \"readTime\": \"10 min read\", \"difficulty\": \"Intermediate\", \"rating\": 4.6, \"publishDate\": \"YYYY-MM-DD\", \"author\": \"...\", \"tags\": [\"tag1\", \"tag2\"]}},\n" \
                         f"  {{\"type\": \"interactive\", \"category\": \"interactive\", \"title\": \"...\", \"description\": \"...\", \"url\": \"https://example.com/tool\", \"thumbnail\": \"https://via.placeholder.com/300x200?text=Interactive\", \"difficulty\": \"All Levels\", \"rating\": 4.7, \"author\": \"...\", \"tags\": [\"tag1\", \"tag2\"], \"features\": [\"feature1\", \"feature2\"]}},\n" \
                         f"  {{\"type\": \"book\", \"category\": \"book\", \"title\": \"...\", \"description\": \"...\", \"url\": \"https://amazon.com/book\", \"thumbnail\": \"https://via.placeholder.com/300x200?text=Book\", \"pages\": 200, \"difficulty\": \"Intermediate\", \"rating\": 4.8, \"author\": \"...\", \"tags\": [\"tag1\", \"tag2\"], \"isbn\": \"978-1234567890\"}}\n" \
                         f"]"

                response_text = self._call_gemini(prompt, model)
                if not response_text or not response_text.strip():
                    logger.warning(f"Empty response from Gemini for {doc_name}, skipping.")
                    continue

                # Strip markdown if present
                response_text = response_text.strip()
                if response_text.startswith('```json'):
                    response_text = response_text[7:].strip()
                if response_text.endswith('```'):
                    response_text = response_text[:-3].strip()

                try:
                    gen_resources = json.loads(response_text)
                    if not isinstance(gen_resources, list) or len(gen_resources) != 6:
                        raise ValueError("Expected a list of 6 resources")
                    for i, res in enumerate(gen_resources):
                        if not all(key in res for key in ['type', 'category', 'title', 'description', 'url']):
                            raise ValueError("Missing required fields in resource")
                        res['id'] = f"{res['type']}-{doc_name}-{i+1}"
                        res['topic'] = doc_name
                    resources_list.extend(gen_resources)
                except (json.JSONDecodeError, ValueError) as e:
                    logger.error(f"Invalid JSON response from Gemini for {doc_name}: {e}. Raw response: {response_text}")
            except Exception as e:
                logger.error(f"Failed to process file {json_file}: {e}")
                continue
        return {"resources": resources_list}

    def generate_quiz(self, topic: str, difficulty: str, model: str) -> List[Dict]:
        """Generate quiz questions using Gemini based on topic."""
        # Find the raw text for the topic
        json_files = list(self.raw_dir.glob("*_text.json"))
        if not json_files:
            logger.error("No processed raw text files found")
            return []

        selected_file = None
        for file in json_files:
            file_topic = file.stem.replace('_text', '')
            if file_topic.lower() == topic.lower().replace('+', ''):
                selected_file = file
                break
        if not selected_file:
            logger.warning(f"Exact topic {topic} not found, using first available file")
            selected_file = json_files[0] if json_files else None

        if not selected_file:
            logger.error("No raw text files available")
            return []

        try:
            with open(selected_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                text = data.get('text', '')
            context = text[:4000]  # Increased limit for more context
            num_questions = 5  # Default to 5 questions
            if difficulty == 'easy':
                q_types = 'multiple-choice'
            elif difficulty == 'medium':
                q_types = 'mix of multiple-choice and short-answer'
            else:
                q_types = 'mix of multiple-choice, short-answer, and long-answer'

            prompt = f"Based on the document topic '{topic}' and content snippet: {context}\n\n" \
                     f"Generate exactly {num_questions} quiz questions of {q_types} type for {difficulty} difficulty.\n" \
                     f"Return ONLY a valid JSON array with {num_questions} objects.\n" \
                     f"For multiple-choice: {{\"id\": 1, \"text\": \"...\", \"options\": [\"A\", \"B\", \"C\", \"D\"], \"answer\": \"A\", \"explanation\": \"...\", \"type\": \"multiple-choice\"}}\n" \
                     f"For short-answer: {{\"id\": 1, \"text\": \"...\", \"sampleAnswer\": \"...\", \"points\": 10, \"type\": \"short-answer\"}}\n" \
                     f"For long-answer: {{\"id\": 1, \"text\": \"...\", \"sampleAnswer\": \"...\", \"points\": 20, \"type\": \"long-answer\"}}\n" \
                     f"Ensure questions are relevant, varied, and include explanations for multiple-choice."

            response_text = self._call_gemini(prompt, model)
            if not response_text or not response_text.strip():
                logger.warning(f"Empty response from Gemini for quiz on {topic}")
                return []

            # Strip markdown if present
            response_text = response_text.strip()
            if response_text.startswith('```json'):
                response_text = response_text[7:].strip()
            if response_text.endswith('```'):
                response_text = response_text[:-3].strip()

            try:
                gen_questions = json.loads(response_text)
                if not isinstance(gen_questions, list) or len(gen_questions) != num_questions:
                    raise ValueError(f"Expected a list of {num_questions} questions, got {len(gen_questions)}")
                for q in gen_questions:
                    if 'type' not in q or 'text' not in q:
                        raise ValueError("Missing required fields in question")
                    if q['type'] == 'multiple-choice' and ('options' not in q or 'answer' not in q or 'explanation' not in q):
                        raise ValueError("Missing required fields in multiple-choice question")
                return gen_questions
            except (json.JSONDecodeError, ValueError) as e:
                logger.error(f"Invalid JSON response from Gemini for quiz on {topic}: {e}. Raw response: {response_text}")
                return []
        except Exception as e:
            logger.error(f"Failed to generate quiz for {topic}: {e}")
            return []

    def _call_gemini(self, prompt: str, model: str) -> str:
        """Internal method to call Gemini with retry logic."""
        max_retries = 3
        for attempt in range(max_retries):
            try:
                model_instance = genai.GenerativeModel(model)
                response = model_instance.generate_content(prompt)
                return response.text
            except Exception as e:
                logger.error(f"Error calling Gemini: {str(e)}")
                if attempt < max_retries - 1:
                    logger.warning(f"Retrying in 17 seconds (Attempt {attempt + 1}/{max_retries})")
                    time.sleep(17)
                else:
                    return "Failed to generate after retries."
        return "Failed to generate after retries."

if __name__ == "__main__":
    main()
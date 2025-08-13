import json
import os
from pathlib import Path
import logging
import re
import spacy
from typing import List, Dict, Optional

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Load spaCy model
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    logger.warning("spaCy model 'en_core_web_sm' not found. Downloading...")
    spacy.cli.download("en_core_web_sm")
    nlp = spacy.load("en_core_web_sm")

class TextCleaner:
    """Cleans and chunks raw text extracted from PDFs."""
    
    def __init__(self, input_dir: str, output_dir: str, chunk_size: int = 512, overlap: int = 50):
        """Initialize the cleaner with input, output directories, and chunking parameters.
        
        Args:
            input_dir (str): Directory containing raw text JSON files.
            output_dir (str): Directory to store cleaned and chunked text JSON files.
            chunk_size (int): Maximum tokens per chunk (default: 512).
            overlap (int): Number of overlapping tokens between chunks (default: 50).
        """
        self.input_dir = Path(input_dir)
        self.output_dir = Path(output_dir)
        self.chunk_size = chunk_size
        self.overlap = overlap
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def clean_text(self, text: str) -> str:
        """Clean a single text string by removing noise and normalizing whitespace.
        
        Args:
            text (str): Raw text to clean.
        
        Returns:
            str: Cleaned text.
        """
        if not text:
            return ""
        
        text = re.sub(r"^\s*Page\s+\d+\s*$", "", text, flags=re.MULTILINE)
        text = re.sub(r"^\s*-\s*$", "", text, flags=re.MULTILINE)
        text = re.sub(r"\s+", " ", text)
        return text.strip()
    
    def chunk_text(self, text: str) -> List[str]:
        """Split cleaned text into chunks based on token count with overlap.
        
        Args:
            text (str): Cleaned text to chunk.
        
        Returns:
            List[str]: List of text chunks.
        """
        if not text:
            return []
        
        doc = nlp(text)
        tokens = [token.text for token in doc]
        chunks = []
        
        # Create chunks with overlap
        for i in range(0, len(tokens), self.chunk_size - self.overlap):
            end_idx = min(i + self.chunk_size, len(tokens))
            chunk_tokens = tokens[i:end_idx]
            chunk_text = " ".join(chunk_tokens)
            chunks.append(chunk_text)
        
        # Ensure the last chunk has at least overlap tokens if possible
        if len(chunks) > 0 and len(tokens) > self.chunk_size:
            last_chunk_start = max(0, len(tokens) - self.chunk_size)
            if last_chunk_start > 0:
                chunk_tokens = tokens[last_chunk_start:]
                chunk_text = " ".join(chunk_tokens)
                if chunk_text.strip():
                    chunks.append(chunk_text)
        
        return chunks
    
    def process_document(self, json_path: Path) -> Optional[Dict[str, List[str]]]:
        """Clean and chunk text from a single JSON file and return processed data.
        
        Args:
            json_path (Path): Path to the raw text JSON file.
        
        Returns:
            Optional[Dict[str, List[str]]]: Processed document data, or None if processing fails.
        """
        try:
            with json_path.open("r", encoding="utf-8") as f:
                raw_data = json.load(f)
            
            processed_data = {
                "doc_name": raw_data["doc_name"],
                "page_count": raw_data["page_count"],
                "chunks": []
            }
            
            for page_text in raw_data["pages"]:
                cleaned_text = self.clean_text(page_text)
                if cleaned_text:
                    chunks = self.chunk_text(cleaned_text)
                    processed_data["chunks"].extend(chunks)
                else:
                    logger.warning(f"No clean text extracted from page in {json_path}")
            
            # Save processed text as JSON
            output_path = self.output_dir / f"{json_path.stem}_processed.json"
            with output_path.open("w", encoding="utf-8") as f:
                json.dump(processed_data, f, ensure_ascii=False, indent=2)
            logger.info(f"Saved processed text to {output_path}")
            return processed_data
        
        except Exception as e:
            logger.error(f"Error processing {json_path}: {str(e)}")
            return None
    
    def process_all_documents(self) -> List[Dict[str, List[str]]]:
        """Process all JSON files in the input directory.
        
        Returns:
            List[Dict[str, List[str]]]: List of processed document data.
        """
        processed_texts = []
        json_files = list(self.input_dir.glob("*.json"))
        
        if not json_files:
            logger.warning(f"No JSON files found in {self.input_dir}")
            return processed_texts
        
        for json_path in json_files:
            processed_data = self.process_document(json_path)
            if processed_data:
                processed_texts.append(processed_data)
        
        logger.info(f"Processed {len(processed_texts)} documents")
        return processed_texts

def main():
    """Example usage of TextCleaner."""
    input_dir = "data/processed/raw_text"
    output_dir = "data/processed/chunks"
    cleaner = TextCleaner(input_dir, output_dir, chunk_size=512, overlap=50)
    cleaned_texts = cleaner.process_all_documents()

if __name__ == "__main__":
    main()

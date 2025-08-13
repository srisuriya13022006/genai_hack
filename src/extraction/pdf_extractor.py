import fitz  # PyMuPDF
import os
from pathlib import Path
import logging
from typing import List, Dict, Optional

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

class PDFExtractor:
    """Extracts text from PDF files using PyMuPDF, handling multi-page and complex layouts."""
    
    def __init__(self, input_dir: str, output_dir: str):
        """Initialize the extractor with input and output directories.
        
        Args:
            input_dir (str): Directory containing input PDF files.
            output_dir (str): Directory to store extracted text (JSON format).
        """
        self.input_dir = Path(input_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def extract_text(self, pdf_path: str) -> Optional[Dict[str, List[str]]]:
        """Extract text from a single PDF file, preserving page-level information.
        
        Args:
            pdf_path (str): Path to the PDF file.
        
        Returns:
            Optional[Dict[str, List[str]]]: Dictionary with document metadata and page texts,
                                           or None if extraction fails.
        """
        pdf_path = Path(pdf_path)
        if not pdf_path.exists() or not pdf_path.is_file():
            logger.error(f"PDF file not found: {pdf_path}")
            return None
        
        try:
            doc = fitz.open(pdf_path)
            if doc.page_count == 0:
                logger.warning(f"Empty PDF: {pdf_path}")
                doc.close()
                return None
            
            # Store text for each page
            extracted_data = {
                "doc_name": pdf_path.name,
                "page_count": doc.page_count,
                "pages": []
            }
            
            for page_num in range(doc.page_count):
                page = doc.load_page(page_num)
                text = page.get_text("text", sort=True)
                if not text.strip():
                    logger.warning(f"No text extracted from page {page_num + 1} of {pdf_path}")
                    extracted_data["pages"].append("")
                else:
                    extracted_data["pages"].append(text.strip())
            
            doc.close()
            logger.info(f"Successfully extracted text from {pdf_path}")
            return extracted_data
        
        except Exception as e:
            logger.error(f"Error extracting text from {pdf_path}: {str(e)}")
            return None
    
    def process_pdfs(self) -> List[Dict[str, List[str]]]:
        """Process all PDFs in the input directory and its subdirectories, saving extracted text to output directory.
        
        Returns:
            List[Dict[str, List[str]]]: List of extracted data for each PDF.
        """
        extracted_texts = []
        pdf_files = list(self.input_dir.rglob("*.pdf"))  # Use rglob for recursive search
        
        if not pdf_files:
            logger.warning(f"No PDF files found in {self.input_dir} or its subdirectories")
            return extracted_texts
        
        for pdf_path in pdf_files:
            extracted_data = self.extract_text(pdf_path)
            if extracted_data:
                extracted_texts.append(extracted_data)
                # Save extracted text as JSON
                output_path = self.output_dir / f"{pdf_path.stem}_text.json"
                import json
                with output_path.open("w", encoding="utf-8") as f:
                    json.dump(extracted_data, f, ensure_ascii=False, indent=2)
                logger.info(f"Saved extracted text to {output_path}")
        
        return extracted_texts

def main():
    """Example usage of PDFExtractor."""
    input_dir = "data/input"
    output_dir = "data/processed/raw_text"
    extractor = PDFExtractor(input_dir, output_dir)
    extracted_texts = extractor.process_pdfs()
    logger.info(f"Processed {len(extracted_texts)} PDFs")

if __name__ == "__main__":
    main()

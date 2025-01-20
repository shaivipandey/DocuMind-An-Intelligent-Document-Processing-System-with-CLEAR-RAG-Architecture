import PyPDF2
import os
from typing import Dict, Any
import json

def extract_text_from_pdf(file_path: str) -> str:
    """
    Extract text content from a PDF file.
    """
    try:
        text = ""
        with open(file_path, 'rb') as file:
            # Create PDF reader object
            pdf_reader = PyPDF2.PdfReader(file)
            
            # Extract text from each page
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
        
        return text.strip()
    except Exception as e:
        raise Exception(f"Error extracting text from PDF: {str(e)}")

def process_document(file_path: str) -> Dict[str, Any]:
    """
    Process a document: extract text and generate metadata.
    """
    try:
        # Extract text from PDF
        extracted_text = extract_text_from_pdf(file_path)
        
        # Get basic document info
        filename = os.path.basename(file_path)
        file_size = os.path.getsize(file_path)
        
        # Create document metadata
        doc_info = {
            "filename": filename,
            "file_size": file_size,
            "text_length": len(extracted_text),
            "status": "processed"
        }
        
        # Save extracted text
        output_dir = "../output"
        text_file_path = os.path.join(output_dir, f"{filename}.txt")
        with open(text_file_path, "w", encoding="utf-8") as f:
            f.write(extracted_text)
        
        # Update document info
        doc_info["text_file_path"] = text_file_path
        
        # Save updated document info
        info_file_path = os.path.join(output_dir, f"{filename}.json")
        with open(info_file_path, "w") as f:
            json.dump(doc_info, f, indent=2)
        
        return doc_info
    
    except Exception as e:
        raise Exception(f"Error processing document: {str(e)}")

def get_document_text(filename: str) -> str:
    """
    Retrieve processed text for a document.
    """
    try:
        output_dir = "../output"
        text_file_path = os.path.join(output_dir, f"{filename}.txt")
        
        if not os.path.exists(text_file_path):
            raise Exception("Document text not found")
        
        with open(text_file_path, "r", encoding="utf-8") as f:
            return f.read()
    
    except Exception as e:
        raise Exception(f"Error retrieving document text: {str(e)}")

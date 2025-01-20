import PyPDF2
import os
from typing import Dict, Any
import json
from html_processor import html_processor

class DocumentProcessor:
    """
    Process different types of documents (PDF, HTML) and extract their content.
    """
    def __init__(self):
        # Get absolute path to output directory
        self.output_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "output"))
        os.makedirs(self.output_dir, exist_ok=True)
        print(f"Document processor initialized with output directory: {self.output_dir}")  # Debug log

    def extract_text_from_pdf(self, file_path: str) -> str:
        """
        Extract text content from a PDF file.
        """
        try:
            print(f"Opening PDF file: {file_path}")  # Debug log
            if not os.path.exists(file_path):
                raise Exception(f"PDF file not found at path: {file_path}")
                
            text = ""
            with open(file_path, 'rb') as file:
                # Create PDF reader object
                pdf_reader = PyPDF2.PdfReader(file)
                print(f"PDF has {len(pdf_reader.pages)} pages")  # Debug log
                
                # Extract text from each page
                for i, page in enumerate(pdf_reader.pages):
                    page_text = page.extract_text()
                    text += page_text + "\n"
                    print(f"Extracted {len(page_text)} characters from page {i+1}")  # Debug log
            
            return text.strip()
        except Exception as e:
            raise Exception(f"Error extracting text from PDF: {str(e)}")

    def get_file_type(self, file_path: str) -> str:
        """
        Determine the type of file based on extension.
        """
        extension = file_path.lower().split('.')[-1]
        if extension == 'pdf':
            return 'pdf'
        elif extension in ['html', 'htm']:
            return 'html'
        else:
            raise ValueError(f"Unsupported file type: {extension}")

    def process_document(self, file_path: str) -> Dict[str, Any]:
        """
        Process a document: extract text and generate metadata based on file type.
        """
        try:
            # Ensure output directory exists
            os.makedirs(self.output_dir, exist_ok=True)
            
            file_type = self.get_file_type(file_path)
            print(f"Processing {file_type} file: {file_path}")  # Debug log
            
            if file_type == 'pdf':
                print(f"Starting PDF text extraction from: {file_path}")  # Debug log
                
                # Extract text from PDF
                extracted_text = self.extract_text_from_pdf(file_path)
                print(f"Extracted {len(extracted_text)} characters of text")  # Debug log
                
                # Get basic document info
                filename = os.path.basename(file_path)
                file_size = os.path.getsize(file_path)
                print(f"Processing PDF: {filename} ({file_size} bytes)")  # Debug log
                
                # Create document metadata
                doc_info = {
                    "filename": filename,
                    "file_type": "pdf",
                    "file_size": file_size,
                    "text_length": len(extracted_text),
                    "status": "processed"
                }
                
                try:
                    # Save extracted text
                    text_file_path = os.path.join(self.output_dir, f"{filename}.txt")
                    print(f"Saving PDF text to: {text_file_path}")  # Debug log
                    with open(text_file_path, "w", encoding="utf-8") as f:
                        f.write(extracted_text)
                except Exception as e:
                    print(f"Error saving PDF text: {str(e)}")  # Debug log
                    raise
                
                # Update document info
                doc_info["text_file_path"] = text_file_path
                
                try:
                    # Save updated document info
                    info_file_path = os.path.join(self.output_dir, f"{filename}.json")
                    print(f"Saving PDF info to: {info_file_path}")  # Debug log
                    with open(info_file_path, "w") as f:
                        json.dump(doc_info, f, indent=2)
                except Exception as e:
                    print(f"Error saving PDF info: {str(e)}")  # Debug log
                    raise
                
                return doc_info
            
            elif file_type == 'html':
                try:
                    # Use HTML processor for HTML files
                    result = html_processor.process(file_path)
                    print(f"HTML processing result: {result}")  # Debug log
                    
                    # Add filename to result for consistency with PDF processing
                    result["filename"] = os.path.basename(file_path)
                    return result
                except Exception as e:
                    print(f"HTML processing error: {str(e)}")  # Debug log
                    raise
            
        except Exception as e:
            raise Exception(f"Error processing document: {str(e)}")

    def get_document_text(self, filename: str) -> str:
        """
        Retrieve processed text for a document.
        """
        try:
            text_file_path = os.path.join(self.output_dir, f"{filename}.txt")
            
            if not os.path.exists(text_file_path):
                raise Exception("Document text not found")
            
            with open(text_file_path, "r", encoding="utf-8") as f:
                return f.read()
        
        except Exception as e:
            raise Exception(f"Error retrieving document text: {str(e)}")

# Create a global instance
document_processor = DocumentProcessor()
